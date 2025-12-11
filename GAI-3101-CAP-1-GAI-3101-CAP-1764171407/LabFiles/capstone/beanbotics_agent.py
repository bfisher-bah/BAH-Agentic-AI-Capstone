"""
BeanBotics Support Agent - MVP
An automated ticket classification and processing system for BeanBotics Inc.

This agent:
1. Fetches unprocessed tickets from the ticketing system API
2. Classifies tickets into categories (Mechanical, Quality, Maintenance, etc.)
3. Assigns priority levels (High, Medium, Low)
4. Updates tickets in the system via API

Usage:
    python beanbotics_agent.py
"""

import os
import json
import requests
from typing import TypedDict, Optional, List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

# Load environment variables
load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

API_BASE_URL = os.getenv("TICKETING_API_URL", "http://localhost:3000")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

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
    # Processing log
    log: List[str]
    # Error tracking
    errors: List[str]


# =============================================================================
# LLM Setup
# =============================================================================

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.0)


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


def update_ticket(state: AgentState) -> AgentState:
    """Update the ticket in the API with category and priority."""
    ticket = state.get("current_ticket")
    category = state.get("classified_category")
    priority = state.get("assigned_priority")
    log = state.get("log", [])
    errors = state.get("errors", [])

    if not ticket or not category or not priority:
        return state

    log.append(f"[UPDATE] Updating ticket {ticket['id']}...")

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/tickets/{ticket['id']}",
            json={
                "category": category,
                "priority": priority,
            },
            timeout=10
        )
        response.raise_for_status()

        log.append(f"[UPDATE] Success! Ticket updated with category='{category}', priority='{priority}'")

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

    # Main processing flow
    workflow.add_edge("classify", "prioritize")
    workflow.add_edge("prioritize", "update")
    workflow.add_edge("update", "increment")
    workflow.add_edge("increment", "select_next")

    return workflow.compile()


# =============================================================================
# Main Entry Point
# =============================================================================

def run_agent():
    """Run the BeanBotics support agent."""
    print("=" * 60)
    print("BeanBotics Support Agent - MVP")
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


if __name__ == "__main__":
    run_agent()