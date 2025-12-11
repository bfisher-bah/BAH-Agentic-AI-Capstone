"""
BeanBotics Support Agent
An automated ticket classification and processing system for BeanBotics Inc.

This agent:
1. Fetches unprocessed tickets from the ticketing system API
2. Classifies tickets into categories (Mechanical, Quality, Maintenance, etc.)
3. Assigns priority levels (High, Medium, Low)
4. Extracts serial numbers from ticket descriptions
5. Uses RAG to generate troubleshooting responses from support documentation
6. Updates tickets and posts responses via API

Modes:
    - Batch mode: Process all unprocessed tickets once and exit
    - WebSocket mode: Listen for new tickets in real-time and process them as they arrive

Usage:
    # Batch mode (default):
    python beanbotics_agent.py

    # WebSocket real-time mode:
    python beanbotics_agent.py --watch

    # From Jupyter/SageMaker:
    from beanbotics_agent import run_agent, run_agent_websocket
    run_agent()  # Batch mode
    await run_agent_websocket()  # Real-time mode

Configuration:
    Edit secrets.env with your OpenAI API key and other settings.
"""

import os
import re
import json
import asyncio
import requests
from pathlib import Path
from typing import TypedDict, Optional, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.graph import StateGraph, START, END

# WebSocket import (optional, for real-time mode)
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

# Load environment variables from secrets.env
secrets_path = Path(__file__).parent / "secrets.env"
load_dotenv(secrets_path)

# Configuration
API_BASE_URL = os.environ.get("TICKETING_API_URL", "http://localhost:3000")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")

# Classification categories based on support documentation
CATEGORIES = [
    "Mechanical",           # Machine not grinding, motors, physical issues
    "Coffee Quality",       # Taste issues, consistency problems
    "Maintenance",          # Cleaning cycles, drip tray, descaling, leaks
    "Technical",            # Software updates, connectivity, errors
    "Power/Startup",        # Machine won't turn on, power issues
    "Installation/Setup",   # Initial setup, registration, calibration
    "Feature Request",      # Customer suggestions for new features
    "General Inquiry",      # Warranty, training, documentation questions
]

# Priority levels
PRIORITIES = ["High", "Medium", "Low"]

# =============================================================================
# Agent State Schema
# =============================================================================

class TicketData(TypedDict):
    """Structure for a single ticket from the API."""
    id: str
    created_at: str
    customer_name: str
    customer_email: str
    subject: str
    serial_number: str
    description: str
    category: str
    priority: str
    status: str


class AgentState(TypedDict):
    """State that flows through the LangGraph workflow."""
    # List of tickets to process
    tickets: List[TicketData]
    # Index of current ticket being processed
    current_index: int
    # Current ticket data
    current_ticket: Optional[TicketData]
    # Classification result
    classified_category: Optional[str]
    # Priority result
    assigned_priority: Optional[str]
    # Extracted serial number
    extracted_serial: Optional[str]
    # RAG-generated response
    rag_response: Optional[str]
    # Missing information fields
    missing_info: Optional[List[str]]
    # Escalation flag and reason
    needs_escalation: bool
    escalation_reason: Optional[str]
    # Processing log
    log: List[str]
    # Error tracking
    errors: List[str]


# =============================================================================
# Serial Number Extraction & Generation
# =============================================================================

# Common serial number patterns for Bean Machine
# Examples: BM-1001, BM-2345, BM1001, etc.
SERIAL_PATTERNS = [
    r'\bBM-?\d{4,6}\b',           # BM-1001 or BM1001
    r'\bBean\s*Machine\s*#?\s*\d{4,6}\b',  # Bean Machine #1001
    r'\bserial\s*(?:number|#|:)?\s*(\w{2,3}-?\d{4,6})\b',  # serial number: XX-1234
    r'\bS/N\s*:?\s*(\w{2,3}-?\d{4,6})\b',  # S/N: XX-1234
]

def extract_serial_number(text: str) -> Optional[str]:
    """
    Extract a serial number from ticket text.
    Returns the first matching serial number or None.
    """
    if not text:
        return None

    for pattern in SERIAL_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Return the captured group if present, otherwise the full match
            serial = match.group(1) if match.lastindex else match.group(0)
            # Normalize: uppercase, ensure hyphen format
            serial = serial.upper().strip()
            # Add hyphen if missing (BM1001 -> BM-1001)
            if re.match(r'^BM\d', serial):
                serial = 'BM-' + serial[2:]
            return serial

    return None


def generate_serial_number(ticket_id: str) -> str:
    """
    Generate a serial number for tickets that don't have one.
    Uses a deterministic approach based on ticket ID to ensure consistency.

    Format: BM-XXXX where XXXX is derived from the ticket ID
    """
    import hashlib
    # Create a hash of the ticket ID and take first 4 digits
    hash_digest = hashlib.md5(ticket_id.encode()).hexdigest()
    # Convert hex to decimal and take last 4 digits, ensuring range 1000-9999
    numeric_part = (int(hash_digest[:8], 16) % 9000) + 1000
    return f"BM-{numeric_part}"


# =============================================================================
# LLM Setup
# =============================================================================

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.0)


# =============================================================================
# RAG System Setup
# =============================================================================

def _find_support_docs_path() -> Path:
    """
    Find the support-info directory, handling both script and notebook execution.
    """
    # Try multiple possible locations
    possible_paths = [
        # When running as a script
        Path(__file__).parent / "support-info" if '__file__' in dir() else None,
        # Current working directory
        Path.cwd() / "support-info",
        # Parent of current directory (if running from a subdirectory)
        Path.cwd().parent / "support-info",
        # Explicit capstone path
        Path.cwd() / "capstone" / "support-info",
        # For Jupyter notebooks - look relative to notebook location
        Path("support-info"),
        Path("./support-info"),
    ]

    for path in possible_paths:
        if path is not None and path.exists() and path.is_dir():
            return path

    # Default fallback
    return Path("support-info")


# Path to support documentation (resolved at runtime)
SUPPORT_DOCS_PATH = _find_support_docs_path()

# Global vector store (initialized lazily)
_vector_store = None

def get_retriever():
    """
    Initialize and return the RAG retriever.
    Uses lazy initialization to avoid loading docs until needed.
    """
    global _vector_store, SUPPORT_DOCS_PATH

    if _vector_store is None:
        # Re-resolve path in case it wasn't found at module load time
        SUPPORT_DOCS_PATH = _find_support_docs_path()

        print(f"[RAG] Loading support documentation from: {SUPPORT_DOCS_PATH}")

        if not SUPPORT_DOCS_PATH.exists():
            print(f"[RAG ERROR] Support docs directory not found: {SUPPORT_DOCS_PATH}")
            print(f"[RAG] Current working directory: {Path.cwd()}")
            return None

        try:
            # Load all markdown files from support-info directory
            # Use TextLoader instead of default UnstructuredLoader to avoid unstructured dependency
            loader = DirectoryLoader(
                str(SUPPORT_DOCS_PATH),
                glob="**/*.md",
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"},
                show_progress=False
            )
            docs = loader.load()

            if not docs:
                print(f"[RAG ERROR] No markdown files found in {SUPPORT_DOCS_PATH}")
                return None

            print(f"[RAG] Loaded {len(docs)} support documents")

            # Create embeddings and vector store
            embeddings = OpenAIEmbeddings()
            _vector_store = InMemoryVectorStore(embeddings)
            _vector_store.add_documents(docs)
            print("[RAG] Vector store initialized")

        except Exception as e:
            print(f"[RAG ERROR] Failed to initialize RAG system: {e}")
            import traceback
            traceback.print_exc()
            return None

    return _vector_store.as_retriever()


# =============================================================================
# Workflow Nodes
# =============================================================================

def fetch_tickets(state: AgentState) -> AgentState:
    """
    Fetch all tickets from the API and filter for unprocessed ones.
    Unprocessed = missing category or priority.
    """
    log = state.get("log", [])
    errors = state.get("errors", [])

    log.append("[FETCH] Fetching tickets from API...")

    try:
        response = requests.get(f"{API_BASE_URL}/api/tickets", timeout=10)
        response.raise_for_status()
        all_tickets = response.json()

        # Filter for unprocessed tickets (empty category or priority)
        unprocessed = [
            t for t in all_tickets
            if not t.get("category") or not t.get("priority")
        ]

        log.append(f"[FETCH] Found {len(all_tickets)} total tickets, {len(unprocessed)} need processing")

        return {
            **state,
            "tickets": unprocessed,
            "current_index": 0,
            "log": log,
            "errors": errors,
        }

    except requests.RequestException as e:
        errors.append(f"[FETCH ERROR] Failed to fetch tickets: {e}")
        log.append(f"[FETCH] Error: {e}")
        return {
            **state,
            "tickets": [],
            "current_index": 0,
            "log": log,
            "errors": errors,
        }


def select_next_ticket(state: AgentState) -> AgentState:
    """Select the next ticket to process from the queue."""
    tickets = state.get("tickets", [])
    current_index = state.get("current_index", 0)
    log = state.get("log", [])

    if current_index < len(tickets):
        ticket = tickets[current_index]
        log.append(f"\n[SELECT] Processing ticket {current_index + 1}/{len(tickets)}: {ticket['id']}")
        log.append(f"[SELECT] Subject: {ticket['subject']}")
        return {
            **state,
            "current_ticket": ticket,
            "classified_category": None,
            "assigned_priority": None,
            "log": log,
        }
    else:
        log.append("\n[SELECT] No more tickets to process")
        return {
            **state,
            "current_ticket": None,
            "log": log,
        }


def classify_ticket(state: AgentState) -> AgentState:
    """Use LLM to classify the ticket into a category."""
    ticket = state.get("current_ticket")
    log = state.get("log", [])
    errors = state.get("errors", [])

    if not ticket:
        return state

    log.append("[CLASSIFY] Analyzing ticket content...")

    # Build the classification prompt
    categories_list = "\n".join(f"- {cat}" for cat in CATEGORIES)

    prompt = f"""You are a support ticket classifier for BeanBotics Inc., maker of the "Bean Machine" coffee robot.

Classify the following support ticket into exactly ONE of these categories:
{categories_list}

TICKET INFORMATION:
- Subject: {ticket['subject']}
- Description: {ticket.get('description', 'No description provided')}
- Customer: {ticket['customer_name']}

Respond with ONLY the category name, nothing else. Choose the single most appropriate category."""

    try:
        response = llm.invoke(prompt)
        category = response.content.strip()

        # Validate the category
        if category not in CATEGORIES:
            # Try to match partial/close matches
            category_lower = category.lower()
            for valid_cat in CATEGORIES:
                if valid_cat.lower() in category_lower or category_lower in valid_cat.lower():
                    category = valid_cat
                    break
            else:
                # Default if no match
                log.append(f"[CLASSIFY] Warning: LLM returned '{category}', defaulting to 'General Inquiry'")
                category = "General Inquiry"

        log.append(f"[CLASSIFY] Category: {category}")

        return {
            **state,
            "classified_category": category,
            "log": log,
        }

    except Exception as e:
        errors.append(f"[CLASSIFY ERROR] {e}")
        log.append(f"[CLASSIFY] Error: {e}")
        return {
            **state,
            "classified_category": "General Inquiry",  # Safe default
            "log": log,
            "errors": errors,
        }


def assign_priority(state: AgentState) -> AgentState:
    """Use LLM to assign priority based on ticket content and category."""
    ticket = state.get("current_ticket")
    category = state.get("classified_category")
    log = state.get("log", [])
    errors = state.get("errors", [])

    if not ticket:
        return state

    log.append("[PRIORITY] Determining priority level...")

    prompt = f"""You are a support ticket prioritizer for BeanBotics Inc.

Assign a priority level to this ticket based on:
- High: Safety concerns, machine completely non-functional, water leaks, urgent language, business impact
- Medium: Partial functionality issues, quality concerns, general problems affecting usage
- Low: Feature requests, general inquiries, non-urgent questions

TICKET INFORMATION:
- Subject: {ticket['subject']}
- Description: {ticket.get('description', 'No description provided')}
- Category: {category}
- Customer: {ticket['customer_name']}

Respond with ONLY one word: High, Medium, or Low"""

    try:
        response = llm.invoke(prompt)
        priority = response.content.strip()

        # Validate priority
        if priority not in PRIORITIES:
            priority_lower = priority.lower()
            if "high" in priority_lower:
                priority = "High"
            elif "medium" in priority_lower:
                priority = "Medium"
            else:
                priority = "Low"

        log.append(f"[PRIORITY] Priority: {priority}")

        return {
            **state,
            "assigned_priority": priority,
            "log": log,
        }

    except Exception as e:
        errors.append(f"[PRIORITY ERROR] {e}")
        log.append(f"[PRIORITY] Error: {e}")
        return {
            **state,
            "assigned_priority": "Medium",  # Safe default
            "log": log,
            "errors": errors,
        }


def extract_serial(state: AgentState) -> AgentState:
    """Extract or generate serial number for ticket if not already present."""
    ticket = state.get("current_ticket")
    log = state.get("log", [])

    if not ticket:
        return state

    # Check if ticket already has a serial number
    existing_serial = ticket.get("serial_number", "").strip()
    if existing_serial:
        log.append(f"[SERIAL] Ticket already has serial number: {existing_serial}")
        return {
            **state,
            "extracted_serial": None,  # Don't overwrite existing
            "log": log,
        }

    # Try to extract from subject and description
    combined_text = f"{ticket.get('subject', '')} {ticket.get('description', '')}"
    extracted = extract_serial_number(combined_text)

    if extracted:
        log.append(f"[SERIAL] Extracted serial number from ticket: {extracted}")
    else:
        # Generate a serial number if none found
        extracted = generate_serial_number(ticket.get("id", "unknown"))
        log.append(f"[SERIAL] Generated serial number: {extracted}")

    return {
        **state,
        "extracted_serial": extracted,
        "log": log,
    }


def generate_rag_response(state: AgentState) -> AgentState:
    """
    Use RAG to retrieve relevant support documentation and generate
    a helpful troubleshooting response for the customer.
    """
    ticket = state.get("current_ticket")
    category = state.get("classified_category")
    log = state.get("log", [])
    errors = state.get("errors", [])

    if not ticket:
        return state

    log.append("[RAG] Retrieving relevant support documentation...")

    # Get the retriever
    retriever = get_retriever()
    if retriever is None:
        log.append("[RAG] Skipping - RAG system not available")
        return {
            **state,
            "rag_response": None,
            "log": log,
        }

    try:
        # Build query from ticket content
        query = f"{ticket['subject']} {ticket.get('description', '')}"

        # Retrieve relevant documents
        docs = retriever.invoke(query)
        if not docs:
            log.append("[RAG] No relevant documents found")
            return {
                **state,
                "rag_response": None,
                "log": log,
            }

        log.append(f"[RAG] Found {len(docs)} relevant document(s)")

        # Combine retrieved content
        context = "\n\n".join([doc.page_content for doc in docs[:3]])  # Top 3 docs

        # Generate response using LLM
        prompt = f"""You are a helpful support agent for BeanBotics Inc., maker of the "Bean Machine" coffee robot.

Based on the support documentation below, write a helpful response to the customer's support ticket.
Be friendly, professional, and provide specific troubleshooting steps if applicable.
Keep the response concise (2-4 paragraphs).

SUPPORT DOCUMENTATION:
{context}

CUSTOMER TICKET:
- Subject: {ticket['subject']}
- Description: {ticket.get('description', 'No description provided')}
- Category: {category}
- Customer Name: {ticket['customer_name']}

Write a response that:
1. Acknowledges their issue
2. Provides relevant troubleshooting steps from the documentation
3. Offers next steps or asks clarifying questions if needed
4. Signs off professionally as "BeanBot - BeanBotics Support"

RESPONSE:"""

        response = llm.invoke(prompt)
        rag_response = response.content.strip()

        log.append("[RAG] Generated troubleshooting response")

        return {
            **state,
            "rag_response": rag_response,
            "log": log,
        }

    except Exception as e:
        errors.append(f"[RAG ERROR] {e}")
        log.append(f"[RAG] Error generating response: {e}")
        return {
            **state,
            "rag_response": None,
            "log": log,
            "errors": errors,
        }


def post_response(state: AgentState) -> AgentState:
    """Post the RAG-generated response to the ticket."""
    ticket = state.get("current_ticket")
    rag_response = state.get("rag_response")
    log = state.get("log", [])
    errors = state.get("errors", [])

    if not ticket or not rag_response:
        if not rag_response:
            log.append("[RESPONSE] No response to post (RAG skipped or failed)")
        return {
            **state,
            "log": log,
        }

    log.append(f"[RESPONSE] Posting response to ticket {ticket['id']}...")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/tickets/{ticket['id']}/responses",
            json={
                "author": "BeanBot",
                "message": rag_response,
            },
            timeout=10
        )
        response.raise_for_status()

        log.append("[RESPONSE] Successfully posted troubleshooting response")

        return {
            **state,
            "log": log,
        }

    except requests.RequestException as e:
        errors.append(f"[RESPONSE ERROR] Failed to post response: {e}")
        log.append(f"[RESPONSE] Error: {e}")
        return {
            **state,
            "log": log,
            "errors": errors,
        }


def detect_missing_info(state: AgentState) -> AgentState:
    """
    Detect if the ticket is missing critical information needed to resolve the issue.
    If missing info is found, generate a polite request for the customer.
    """
    ticket = state.get("current_ticket")
    category = state.get("classified_category")
    log = state.get("log", [])
    errors = state.get("errors", [])

    if not ticket:
        return state

    log.append("[MISSING INFO] Checking for missing information...")

    missing = []

    # Check for missing serial number (if not already extracted/generated)
    existing_serial = ticket.get("serial_number", "").strip()
    extracted_serial = state.get("extracted_serial")
    if not existing_serial and not extracted_serial:
        missing.append("serial number")

    # Check for vague or missing description
    description = ticket.get("description", "").strip()
    if len(description) < 20:
        missing.append("detailed description of the issue")

    # Category-specific checks
    if category == "Coffee Quality":
        desc_lower = description.lower()
        if "bean" not in desc_lower and "coffee" not in desc_lower:
            missing.append("type/brand of coffee beans being used")
        if "clean" not in desc_lower and "maintenance" not in desc_lower:
            missing.append("when the machine was last cleaned")

    elif category == "Power/Startup":
        desc_lower = description.lower()
        if "light" not in desc_lower and "led" not in desc_lower and "display" not in desc_lower:
            missing.append("status of indicator lights/display")
        if "outlet" not in desc_lower and "plug" not in desc_lower and "power" not in desc_lower:
            missing.append("confirmation that the power outlet works")

    elif category == "Mechanical":
        desc_lower = description.lower()
        if "sound" not in desc_lower and "noise" not in desc_lower:
            missing.append("any unusual sounds the machine makes")

    if missing:
        log.append(f"[MISSING INFO] Found {len(missing)} missing item(s): {', '.join(missing)}")
    else:
        log.append("[MISSING INFO] No critical information missing")

    return {
        **state,
        "missing_info": missing if missing else None,
        "log": log,
    }


def request_missing_info(state: AgentState) -> AgentState:
    """
    If missing information was detected, post a polite request to the customer.
    """
    ticket = state.get("current_ticket")
    missing_info = state.get("missing_info")
    log = state.get("log", [])
    errors = state.get("errors", [])

    if not ticket or not missing_info:
        if not missing_info:
            log.append("[REQUEST INFO] No missing info to request")
        return {
            **state,
            "log": log,
        }

    log.append(f"[REQUEST INFO] Requesting missing information from customer...")

    # Build a friendly request message
    missing_list = "\n".join(f"  • {item.capitalize()}" for item in missing_info)

    message = f"""Hello {ticket['customer_name']},

Thank you for contacting BeanBotics Support! To help us resolve your issue as quickly as possible, could you please provide the following information:

{missing_list}

This will help our team better understand your situation and provide you with the most accurate assistance.

Thank you for your patience!

BeanBot - BeanBotics Support"""

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/tickets/{ticket['id']}/responses",
            json={
                "author": "BeanBot",
                "message": message,
            },
            timeout=10
        )
        response.raise_for_status()

        log.append("[REQUEST INFO] Successfully posted information request")

        return {
            **state,
            "log": log,
        }

    except requests.RequestException as e:
        errors.append(f"[REQUEST INFO ERROR] Failed to post request: {e}")
        log.append(f"[REQUEST INFO] Error: {e}")
        return {
            **state,
            "log": log,
            "errors": errors,
        }


def check_escalation(state: AgentState) -> AgentState:
    """
    Determine if the ticket needs to be escalated to a human agent.
    Escalation criteria:
    - High priority + certain categories
    - Safety concerns mentioned
    - Water leak mentioned
    - Customer frustration/urgency
    - Repeated issues
    """
    ticket = state.get("current_ticket")
    category = state.get("classified_category")
    priority = state.get("assigned_priority")
    log = state.get("log", [])

    if not ticket:
        return state

    log.append("[ESCALATION] Checking escalation criteria...")

    needs_escalation = False
    escalation_reason = None

    description = ticket.get("description", "").lower()
    subject = ticket.get("subject", "").lower()
    combined_text = f"{subject} {description}"

    # Safety-related keywords
    safety_keywords = ["smoke", "burning", "fire", "spark", "shock", "electric", "danger", "unsafe"]
    for keyword in safety_keywords:
        if keyword in combined_text:
            needs_escalation = True
            escalation_reason = f"Safety concern detected: '{keyword}' mentioned"
            break

    # Water leak is always urgent
    if not needs_escalation and ("leak" in combined_text or "water damage" in combined_text or "flooding" in combined_text):
        needs_escalation = True
        escalation_reason = "Water leak or water damage reported"

    # High priority mechanical/power issues
    if not needs_escalation and priority == "High" and category in ["Mechanical", "Power/Startup"]:
        needs_escalation = True
        escalation_reason = f"High priority {category} issue requires technician review"

    # Customer frustration indicators
    frustration_keywords = ["furious", "angry", "terrible", "worst", "lawsuit", "lawyer", "refund", "return", "broken for weeks", "multiple times"]
    for keyword in frustration_keywords:
        if keyword in combined_text:
            needs_escalation = True
            escalation_reason = f"Customer frustration detected: '{keyword}' mentioned"
            break

    # Repeated issues
    if not needs_escalation and ("again" in combined_text or "still" in combined_text or "keeps" in combined_text or "recurring" in combined_text):
        if "not working" in combined_text or "broken" in combined_text or "same issue" in combined_text:
            needs_escalation = True
            escalation_reason = "Recurring/repeated issue reported"

    if needs_escalation:
        log.append(f"[ESCALATION] ⚠️  ESCALATION NEEDED: {escalation_reason}")
    else:
        log.append("[ESCALATION] No escalation needed")

    return {
        **state,
        "needs_escalation": needs_escalation,
        "escalation_reason": escalation_reason,
        "log": log,
    }


def handle_escalation(state: AgentState) -> AgentState:
    """
    If escalation is needed, update the ticket status and post an escalation notice.
    """
    ticket = state.get("current_ticket")
    needs_escalation = state.get("needs_escalation", False)
    escalation_reason = state.get("escalation_reason")
    log = state.get("log", [])
    errors = state.get("errors", [])

    if not ticket or not needs_escalation:
        return {
            **state,
            "log": log,
        }

    log.append("[ESCALATION] Processing escalation...")

    # Post escalation notice to ticket
    message = f"""⚠️ **This ticket has been escalated for human review.**

**Reason:** {escalation_reason}

A member of our support team will review this ticket and reach out to you shortly. We apologize for any inconvenience and appreciate your patience.

If this is an emergency or safety concern, please call our support hotline at 1-800-BEAN-BOT.

BeanBot - BeanBotics Support"""

    try:
        # Post the escalation message
        response = requests.post(
            f"{API_BASE_URL}/api/tickets/{ticket['id']}/responses",
            json={
                "author": "BeanBot",
                "message": message,
            },
            timeout=10
        )
        response.raise_for_status()

        # Update ticket status to escalated
        status_response = requests.post(
            f"{API_BASE_URL}/api/tickets/{ticket['id']}/status",
            json={"status": "escalated"},
            timeout=10
        )
        status_response.raise_for_status()

        log.append("[ESCALATION] Ticket escalated and status updated")

        return {
            **state,
            "log": log,
        }

    except requests.RequestException as e:
        errors.append(f"[ESCALATION ERROR] Failed to process escalation: {e}")
        log.append(f"[ESCALATION] Error: {e}")
        return {
            **state,
            "log": log,
            "errors": errors,
        }


def update_ticket(state: AgentState) -> AgentState:
    """Update the ticket in the API with category, priority, and serial number."""
    ticket = state.get("current_ticket")
    category = state.get("classified_category")
    priority = state.get("assigned_priority")
    serial = state.get("extracted_serial")
    log = state.get("log", [])
    errors = state.get("errors", [])

    if not ticket or not category or not priority:
        return state

    log.append(f"[UPDATE] Updating ticket {ticket['id']}...")

    # Build update payload
    update_data = {
        "category": category,
        "priority": priority,
    }

    # Add serial number if extracted
    if serial:
        update_data["serial_number"] = serial

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/tickets/{ticket['id']}",
            json=update_data,
            timeout=10
        )
        response.raise_for_status()

        update_msg = f"[UPDATE] Success! category='{category}', priority='{priority}'"
        if serial:
            update_msg += f", serial_number='{serial}'"
        log.append(update_msg)

        return {
            **state,
            "log": log,
        }

    except requests.RequestException as e:
        errors.append(f"[UPDATE ERROR] Failed to update ticket {ticket['id']}: {e}")
        log.append(f"[UPDATE] Error: {e}")
        return {
            **state,
            "log": log,
            "errors": errors,
        }


def increment_index(state: AgentState) -> AgentState:
    """Move to the next ticket in the queue."""
    return {
        **state,
        "current_index": state.get("current_index", 0) + 1,
    }


# =============================================================================
# Routing Logic
# =============================================================================

def should_continue(state: AgentState) -> str:
    """Determine if we should process another ticket or end."""
    tickets = state.get("tickets", [])
    current_index = state.get("current_index", 0)

    if current_index < len(tickets):
        return "process_next"
    else:
        return "done"


# =============================================================================
# Build the Workflow Graph
# =============================================================================

def build_agent() -> StateGraph:
    """Construct the LangGraph workflow."""

    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("fetch_tickets", fetch_tickets)
    workflow.add_node("select_next", select_next_ticket)
    workflow.add_node("classify", classify_ticket)
    workflow.add_node("prioritize", assign_priority)
    workflow.add_node("extract_serial", extract_serial)
    workflow.add_node("check_escalation", check_escalation)
    workflow.add_node("handle_escalation", handle_escalation)
    workflow.add_node("detect_missing_info", detect_missing_info)
    workflow.add_node("request_missing_info", request_missing_info)
    workflow.add_node("generate_response", generate_rag_response)
    workflow.add_node("post_response", post_response)
    workflow.add_node("update", update_ticket)
    workflow.add_node("increment", increment_index)

    # Define edges
    workflow.add_edge(START, "fetch_tickets")
    workflow.add_edge("fetch_tickets", "select_next")

    # Conditional: process ticket or end
    workflow.add_conditional_edges(
        "select_next",
        should_continue,
        {
            "process_next": "classify",
            "done": END,
        }
    )

    # Main processing flow:
    # 1. classify -> prioritize -> extract_serial
    # 2. check_escalation -> handle_escalation (if needed)
    # 3. detect_missing_info -> request_missing_info (if needed)
    # 4. generate_response -> post_response
    # 5. update -> increment -> loop
    workflow.add_edge("classify", "prioritize")
    workflow.add_edge("prioritize", "extract_serial")
    workflow.add_edge("extract_serial", "check_escalation")
    workflow.add_edge("check_escalation", "handle_escalation")
    workflow.add_edge("handle_escalation", "detect_missing_info")
    workflow.add_edge("detect_missing_info", "request_missing_info")
    workflow.add_edge("request_missing_info", "generate_response")
    workflow.add_edge("generate_response", "post_response")
    workflow.add_edge("post_response", "update")
    workflow.add_edge("update", "increment")
    workflow.add_edge("increment", "select_next")

    return workflow.compile()


# =============================================================================
# Single Ticket Processing (for WebSocket mode)
# =============================================================================

def process_single_ticket(ticket_id: str) -> dict:
    """
    Process a single ticket by ID.
    Used by WebSocket mode when a new ticket is created.
    """
    print(f"\n[WEBSOCKET] Processing new ticket: {ticket_id}")

    # Fetch the ticket
    try:
        response = requests.get(f"{API_BASE_URL}/api/tickets/{ticket_id}", timeout=10)
        response.raise_for_status()
        ticket = response.json()
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch ticket {ticket_id}: {e}")
        return {"error": str(e)}

    # Check if already processed
    if ticket.get("category") and ticket.get("priority"):
        print(f"[SKIP] Ticket {ticket_id} already processed")
        return {"skipped": True}

    # Build a mini-workflow state with just this ticket
    initial_state: AgentState = {
        "tickets": [ticket],
        "current_index": 0,
        "current_ticket": None,
        "classified_category": None,
        "assigned_priority": None,
        "extracted_serial": None,
        "rag_response": None,
        "missing_info": None,
        "needs_escalation": False,
        "escalation_reason": None,
        "log": [],
        "errors": [],
    }

    # Run the agent
    agent = build_agent()
    final_state = agent.invoke(initial_state)

    # Print log entries
    for entry in final_state.get("log", []):
        print(entry)

    if final_state.get("errors"):
        for error in final_state["errors"]:
            print(f"[ERROR] {error}")

    return final_state


# =============================================================================
# WebSocket Real-Time Mode
# =============================================================================

async def run_agent_websocket():
    """
    Run the agent in WebSocket mode - continuously listen for new tickets
    and process them in real-time.
    """
    if not WEBSOCKETS_AVAILABLE:
        print("[ERROR] websockets library not installed. Install with: pip install websockets")
        return

    ws_url = API_BASE_URL.replace("http://", "ws://").replace("https://", "wss://") + "/ws"

    print("=" * 60)
    print("BeanBotics Support Agent - Real-Time Mode")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print(f"WebSocket URL: {ws_url}")
    print(f"Model: {OPENAI_MODEL}")
    print("=" * 60)
    print("\nListening for new tickets... (Press Ctrl+C to stop)")
    print("-" * 60)

    while True:
        try:
            async with websockets.connect(ws_url) as websocket:
                print("[CONNECTED] WebSocket connection established")

                async for message in websocket:
                    try:
                        data = json.loads(message)
                        ticket_id = data.get("ticketId")
                        update_type = data.get("updateType")

                        print(f"\n[EVENT] {update_type}: {ticket_id}")

                        # Only process newly created tickets
                        if update_type == "created":
                            process_single_ticket(ticket_id)
                        else:
                            print(f"[SKIP] Ignoring {update_type} event")

                    except json.JSONDecodeError:
                        print(f"[WARN] Invalid JSON message: {message}")

        except websockets.ConnectionClosed:
            print("[DISCONNECTED] WebSocket connection closed. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"[ERROR] WebSocket error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


# =============================================================================
# Main Entry Point - Batch Mode
# =============================================================================

def run_agent():
    """Run the BeanBotics support agent in batch mode (process all unprocessed tickets once)."""
    print("=" * 60)
    print("BeanBotics Support Agent - Batch Mode")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print(f"Model: {OPENAI_MODEL}")
    print("=" * 60)

    # Build and run the agent
    agent = build_agent()

    initial_state: AgentState = {
        "tickets": [],
        "current_index": 0,
        "current_ticket": None,
        "classified_category": None,
        "assigned_priority": None,
        "extracted_serial": None,
        "rag_response": None,
        "missing_info": None,
        "needs_escalation": False,
        "escalation_reason": None,
        "log": [],
        "errors": [],
    }

    # Run the workflow
    final_state = agent.invoke(initial_state)

    # Print the log
    print("\n" + "-" * 60)
    print("PROCESSING LOG:")
    print("-" * 60)
    for entry in final_state.get("log", []):
        print(entry)

    # Print any errors
    if final_state.get("errors"):
        print("\n" + "-" * 60)
        print("ERRORS:")
        print("-" * 60)
        for error in final_state["errors"]:
            print(error)

    print("\n" + "=" * 60)
    print("Agent finished.")
    print("=" * 60)

    return final_state


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """Main entry point with CLI argument handling."""
    import sys

    if "--watch" in sys.argv or "-w" in sys.argv:
        # Real-time WebSocket mode
        print("Starting in real-time watch mode...")
        asyncio.run(run_agent_websocket())
    elif "--help" in sys.argv or "-h" in sys.argv:
        print("""
BeanBotics Support Agent

Usage:
    python beanbotics_agent.py           # Batch mode (process all unprocessed tickets)
    python beanbotics_agent.py --watch   # Real-time mode (listen via WebSocket)
    python beanbotics_agent.py --help    # Show this help message

Configuration:
    Edit secrets.env with your settings:
    - OPENAI_API_KEY: Your OpenAI API key
    - OPENAI_MODEL: Model to use (default: gpt-4o)
    - TICKETING_API_URL: Ticketing system URL (default: http://localhost:3000)
""")
    else:
        # Batch mode (default)
        run_agent()


if __name__ == "__main__":
    main()