# BeanBotics Support Agent - Capstone Project Plan

## Project Overview

**Goal:** Build an automated support ticket processing agent for BeanBotics Inc., a company that produces the "Bean Machine" (an automated coffee-making robot).

**Important Note:** This is NOT an interactive chatbot. It's an automated ticket classification and processing system that runs autonomously.

---

## Table of Contents

1. [Phase 1: Environment Setup & Familiarization](#phase-1-environment-setup--familiarization)
2. [Phase 2: Core Agent Architecture Design](#phase-2-core-agent-architecture-design)
3. [Phase 3: Core Feature Implementation](#phase-3-core-feature-implementation)
4. [Phase 4: Optional/Enhanced Features](#phase-4-optionalenhanced-features)
5. [Phase 5: Testing & Validation](#phase-5-testing--validation)
6. [Phase 6: Presentation Preparation](#phase-6-presentation-preparation)
7. [Team Task Distribution](#team-task-distribution-suggestions)
8. [Key Files Reference](#key-files-reference)
9. [Success Criteria](#success-criteria-checklist)

---

## Phase 1: Environment Setup & Familiarization ✅ COMPLETED

### 1.1 Development Environment

- [x] Set up Python virtual environment
- [x] Install required dependencies:
  ```
  langchain==0.3.*
  langchain_openai==0.3.*
  langchain_community
  unstructured[md]==0.17.*
  langgraph==0.4.*
  websockets==15.0.*
  tiktoken
  ```
- [x] Configure OpenAI API key in environment variables
- [x] Test basic LangChain/LangGraph connectivity

### 1.2 Ticketing System Setup

- [x] Navigate to `GAI-3101-CAP-1-GAI-3101-CAP-1764171407/LabFiles/capstone/ticketing-system/`
- [x] Run `npm install` to install Node.js dependencies
- [x] Start the ticketing system with `npm run dev`
- [x] Access the UI at `http://localhost:3000` (or configured port)
- [x] Review the Swagger documentation at `/api/docs`
- [x] Familiarize with the OpenAPI spec at `/api/docs/openapi.json`

### 1.3 Review Existing Resources

- [x] Study `basic-ticket-agent.ipynb` - the starter notebook with key patterns
- [x] Study `LangChain_LangGraph_Chatbot_Template.py` - template for LangGraph workflows
- [x] Review all 7 support documentation files in `support-info/` folder
- [x] Examine sample tickets in `tickets.json` to understand data format

---

## Phase 2: Core Agent Architecture Design ✅ COMPLETED

### 2.1 Define Agent State Schema ✅

Implemented in `beanbotics_agent.py` as `AgentState` TypedDict tracking:

- [x] Current ticket being processed (`current_ticket`)
- [x] Extracted information (customer name, email, serial number, subject, description)
- [x] Classification result (`classified_category`)
- [x] Priority level (`assigned_priority`)
- [ ] Missing information flags (Phase 4)
- [x] Processing status (`log`, `errors`)
- [ ] RAG context (Phase 4)

### 2.2 Define Classification Categories ✅

Implemented in `beanbotics_agent.py` as `CATEGORIES` list:

| Category | Description |
|----------|-------------|
| Mechanical | Machine not grinding, motors, physical issues |
| Coffee Quality | Taste issues, consistency problems |
| Maintenance/Cleaning | Cleaning cycles, drip tray, descaling |
| Technical/Software | Updates, connectivity, errors |
| Power/Startup | Machine won't turn on, power issues |
| Installation/Setup | Initial setup, registration, calibration |
| Feature Request | Customer suggestions for new features |
| General Inquiry | Warranty, training, documentation questions |

### 2.3 Define Priority Levels

| Priority | Urgency Indicators |
|----------|-------------------|
| High | Safety concerns, machine completely down, water leak, urgent language |
| Medium | Partial functionality issues, quality concerns, general problems |
| Low | Feature requests, general inquiries, non-urgent questions |

### 2.4 Design Agent Workflow Graph

Using LangGraph, design a state machine with these nodes:

```
┌─────────────────┐
│  Fetch Tickets  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│ Extract Information │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Check Completeness  │──────────────┐
└────────┬────────────┘              │
         │                           │ (Missing Info)
         │ (Complete)                ▼
         │                  ┌─────────────────┐
         │                  │  Request Info   │
         │                  └─────────────────┘
         ▼
┌─────────────────────┐
│  Classify Ticket    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Assign Priority    │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  RAG Lookup (opt)   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│   Update Ticket     │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Escalate (if needed)│
└─────────────────────┘
```

**Node Descriptions:**

1. **Fetch Tickets** - Get unprocessed tickets from API
2. **Extract Information** - Parse ticket content for key details
3. **Check Completeness** - Verify all required info is present
4. **Classify Ticket** - Determine category based on content
5. **Assign Priority** - Determine urgency level
6. **RAG Lookup** (optional) - Find relevant support documentation
7. **Update Ticket** - Write classification/priority back to API
8. **Request Info** (optional) - Post response asking for missing details
9. **Escalate** (optional) - Flag for human review if unresolvable

---

## Phase 3: Core Feature Implementation ✅ MVP COMPLETED

### 3.1 API Integration Layer

- [x] ~~Create OpenAPI agent using `create_openapi_agent()` from LangChain~~ (Used direct HTTP requests instead)
- [x] ~~Load and reduce the OpenAPI spec using `reduce_openapi_spec()`~~ (Not needed for direct approach)
- [x] ~~Configure `RequestsWrapper` for API calls~~ (Used `requests` library directly)
- [x] Implement ticket fetching (GET /api/tickets) - `fetch_tickets()` node
- [x] Implement ticket updating (POST /api/tickets/:id) - `update_ticket()` node
- [ ] Implement response posting (POST /api/tickets/:id/responses) - Phase 4 (RAG responses)

**API Endpoints Reference:**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/tickets` | List all tickets |
| POST | `/api/tickets` | Create new ticket |
| GET | `/api/tickets/:id` | Get ticket with responses |
| POST | `/api/tickets/:id` | Update ticket fields |
| DELETE | `/api/tickets/:id` | Delete ticket |
| POST | `/api/tickets/:id/responses` | Add response to ticket |
| POST | `/api/tickets/:id/status` | Update ticket status |

### 3.2 Information Extraction

Use the LLM to extract from ticket content:

- [ ] Customer name validation
- [ ] Customer email validation
- [ ] Serial number detection (if provided)
- [ ] Problem description summarization
- [ ] Urgency indicators detection
- [ ] Missing required information identification

### 3.3 Classification Engine ✅

- [x] Create classification prompt with clear category definitions - `classify_ticket()` node
- [ ] Include few-shot examples for each category (enhancement)
- [x] Use structured output to ensure consistent category assignment - validates against `CATEGORIES` list
- [x] Handle edge cases and multi-category scenarios - defaults to "General Inquiry"

### 3.4 Priority Assignment ✅

- [x] Create priority detection prompt - `assign_priority()` node
- [x] Define urgency keywords/patterns for each level - in prompt
- [x] Consider category in priority (e.g., water leaks = high priority) - category passed to LLM
- [x] Handle ambiguous cases with sensible defaults - defaults to "Medium"

### 3.5 Ticket Update Workflow ✅

- [x] Update ticket with extracted category - `update_ticket()` node
- [x] Update ticket with assigned priority - `update_ticket()` node
- [ ] Update ticket status as appropriate (enhancement)
- [x] Log all actions for audit trail - `log` array in state

---

## Phase 4: Optional/Enhanced Features

### 4.1 Serial Number Extraction ✅ NEW - IMPLEMENTED

- [x] Extract serial numbers from ticket subject/description using regex patterns
- [x] Support multiple formats: BM-1001, BM1001, "serial number: XX-1234", "S/N: XX-1234"
- [x] Normalize extracted serial numbers (uppercase, hyphen format)
- [x] Only extract if ticket doesn't already have a serial number
- [x] Update ticket with extracted serial number via API

### 4.2 Missing Information Handling ✅ IMPLEMENTED

- [x] Detect incomplete tickets (missing serial number, vague descriptions) - `detect_missing_info()` node
- [x] Category-specific checks (Coffee Quality needs bean info, Power/Startup needs indicator light status, etc.)
- [x] Generate polite response requesting specific missing details - `request_missing_info()` node
- [x] Post response via API to ticket thread

### 4.3 RAG System Integration ✅ IMPLEMENTED

- [x] Load support documentation from `support-info/` using `DirectoryLoader` - `get_retriever()`
- [x] Create vector store using `InMemoryVectorStore` with OpenAI embeddings
- [x] Implement semantic search for relevant documentation - `retriever.invoke(query)`
- [x] Generate suggested troubleshooting steps based on retrieved docs - `generate_rag_response()` node
- [x] Post documentation-based suggestions as ticket responses - `post_response()` node

**Support Documentation Available:**

| File | Category |
|------|----------|
| `machine-wont-start.md` | Power/Startup Issues |
| `software-update.md` | Software/Firmware Updates |
| `feature-request.md` | Feature Requests |
| `coffee-quality.md` | Coffee Quality Issues |
| `general-inquiry.md` | General Inquiries |
| `cleaning-maintenance.md` | Cleaning/Maintenance |
| `installation-setup.md` | Installation/Setup |

### 4.4 WebSocket Real-Time Integration ✅ IMPLEMENTED

- [x] Implement async WebSocket listener for real-time ticket updates - `run_agent_websocket()`
- [x] Handle `created` events to process new tickets immediately
- [x] Handle `response` events to follow up when customers reply - `process_customer_response()`
- [x] Auto-reconnect on connection loss with 5-second retry
- [x] CLI flag `--watch` to enable real-time mode

**WebSocket Events:**

- `created` - New ticket submitted ✅ Handled - full processing
- `response` - New response on ticket ✅ Handled - generates follow-up if we asked for info
- `updated` - Ticket fields modified (skipped)
- `deleted` - Ticket removed (skipped)
- `status` - Ticket status updated (skipped)

### 4.5 Escalation Logic ✅ IMPLEMENTED

- [x] Define escalation criteria - `check_escalation()` node:
  - Safety concerns (smoke, burning, fire, spark, shock, danger)
  - Water leak or water damage
  - High priority Mechanical or Power/Startup issues
  - Customer frustration indicators (furious, angry, lawsuit, refund)
  - Recurring/repeated issues
- [x] Update ticket status to "escalated" when criteria met - `handle_escalation()` node
- [x] Generate escalation notice with reason for human agents
- [x] Post escalation message to ticket with support hotline info

**Escalation Teams by Category:**

| Category | Escalation Team |
|----------|-----------------|
| Mechanical | Field service team |
| Coffee Quality | Product quality team |
| Technical/Software | Software engineering team |
| Maintenance | Maintenance specialist |
| Installation | Installation team |

---

## Phase 5: Testing & Validation

### 5.1 Unit Testing

- [ ] Test information extraction with various ticket formats
- [ ] Test classification accuracy for each category
- [ ] Test priority assignment logic
- [ ] Test API integration (CRUD operations)

### 5.2 Integration Testing

- [ ] Process sample tickets end-to-end
- [ ] Verify correct category assignment for all sample tickets
- [ ] Verify correct priority assignment
- [ ] Test missing information detection and response generation
- [ ] Test RAG retrieval accuracy

### 5.3 Edge Case Testing

- [ ] Multi-category tickets (e.g., coffee quality AND cleaning)
- [ ] Tickets with minimal information
- [ ] Tickets with contradictory urgency signals
- [ ] Tickets in different writing styles/formats

### 5.4 Sample Tickets for Testing

The system includes 4 pre-populated sample tickets:

| Ticket ID | Subject | Expected Category | Expected Priority |
|-----------|---------|-------------------|-------------------|
| 1a2b3c4d-0001 | Machine not grinding beans | Mechanical | High |
| 1a2b3c4d-0002 | Coffee tastes bitter | Quality | Medium |
| 1a2b3c4d-0003 | Water leak detected | Maintenance | High |
| 1a2b3c4d-0004 | Machine not responding | Technical | High |

---

## Phase 6: Presentation Preparation

### 6.1 Presentation Content

Using the provided PowerPoint template (`CapstoneMisc/BAH Team Presentation Template.pptx`), prepare slides covering:

- [ ] **Problem Statement** - Why BeanBotics needs automated ticket processing
- [ ] **Solution Overview** - High-level architecture diagram
- [ ] **Technical Architecture** - LangChain/LangGraph components, API integration
- [ ] **Agent Workflow** - Visual flow of ticket processing steps
- [ ] **Classification System** - Categories and how they're determined
- [ ] **RAG Integration** - How support docs enhance responses
- [ ] **Demo Results** - Before/after showing agent processing tickets
- [ ] **Challenges & Solutions** - What was difficult, how you solved it
- [ ] **Future Enhancements** - What else could be added
- [ ] **Lessons Learned** - Key takeaways from the project

### 6.2 Live Demo Preparation

- [ ] Prepare fresh tickets for live classification demo
- [ ] Have fallback screenshots/recordings in case of technical issues
- [ ] Prepare 2-3 different ticket scenarios to demonstrate
- [ ] Show before/after states in the ticketing system UI
- [ ] Be prepared to explain any classification decisions

### 6.3 Demo Script Outline

1. Show empty/unprocessed ticket in UI
2. Run the agent
3. Show the ticket now has category and priority assigned
4. (If RAG implemented) Show the troubleshooting response added
5. (If missing info implemented) Show a ticket requesting more details
6. Explain the decision-making process

---

## Team Task Distribution Suggestions

| Role | Responsibilities |
|------|-----------------|
| **API/Integration Lead** | OpenAPI agent setup, ticketing system integration, WebSocket |
| **Classification Engineer** | Category definitions, prompts, classification accuracy tuning |
| **RAG/Knowledge Lead** | Vector store setup, documentation loading, retrieval tuning |
| **Testing/QA** | Test case creation, validation, edge case handling |
| **Presentation Lead** | Slides, demo script, presentation flow |

### Suggested Sprint Breakdown

**Sprint 1: Foundation**
- Environment setup (all team members)
- Study existing resources (all team members)
- Architecture design decisions (team discussion)

**Sprint 2: Core MVP**
- API integration
- Basic classification
- Priority assignment
- Ticket updating

**Sprint 3: Enhanced Features**
- Missing information handling
- RAG integration
- WebSocket (if time permits)

**Sprint 4: Polish & Present**
- Testing and bug fixes
- Presentation creation
- Demo rehearsal

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `GAI-3101-CAP-1-GAI-3101-CAP-1764171407/GAI-3101-CAP-LabGuide.pdf` | Official requirements document |
| `GAI-3101-CAP-1-GAI-3101-CAP-1764171407/LabFiles/capstone/basic-ticket-agent.ipynb` | Starter code with key patterns |
| `CapstoneMisc/LangChain_LangGraph_Chatbot_Template.py` | LangGraph state management template |
| `GAI-3101-CAP-1-GAI-3101-CAP-1764171407/LabFiles/capstone/ticketing-system/index.js` | API endpoints and schemas |
| `GAI-3101-CAP-1-GAI-3101-CAP-1764171407/LabFiles/capstone/ticketing-system/tickets.json` | Sample tickets for testing |
| `GAI-3101-CAP-1-GAI-3101-CAP-1764171407/LabFiles/capstone/support-info/*.md` | RAG knowledge base (7 documents) |
| `CapstoneMisc/BAH Team Presentation Template.pptx` | Presentation template |

---

## Success Criteria Checklist

### Minimum Viable Product (MVP) ✅ IMPLEMENTED

- [x] Agent reads tickets from API - `fetch_tickets()` node
- [x] Agent correctly classifies tickets into categories - `classify_ticket()` node
- [x] Agent assigns appropriate priority levels - `assign_priority()` node
- [x] Agent updates tickets in the system - `update_ticket()` node

### Enhanced Version ✅ FULLY IMPLEMENTED

- [x] Agent extracts/generates serial numbers - `extract_serial()` node
- [x] Agent requests missing information from customers - `detect_missing_info()` + `request_missing_info()` nodes
- [x] Agent uses RAG to provide troubleshooting guidance - `generate_rag_response()` + `post_response()` nodes
- [x] Agent escalates complex issues appropriately - `check_escalation()` + `handle_escalation()` nodes
- [x] Agent monitors real-time updates via WebSocket - `run_agent_websocket()` with `--watch` flag

### Presentation

- [ ] Uses provided PowerPoint template
- [ ] Demonstrates working agent with live/recorded demo
- [ ] Explains architecture and design decisions clearly
- [ ] Shows measurable results (classification accuracy, etc.)

---

## Discussion Questions for Team

1. **Architecture:** Should we use a single monolithic agent or separate specialized agents for classification, RAG, etc.?

2. **Classification:** How do we handle tickets that fit multiple categories? Pick the primary one, or list multiple?

3. **Priority:** Should priority be purely rule-based, or should the LLM have flexibility to adjust based on context?

4. **RAG:** Do we want the agent to automatically respond with troubleshooting steps, or just classify and let humans respond?

5. **Scope:** Which optional features should we prioritize if time is limited?
   - Missing information requests
   - RAG integration
   - WebSocket real-time processing
   - Escalation logic

6. **Testing:** How will we measure classification accuracy? What's our target accuracy?

7. **Presentation:** Who will present which sections? Do we want a live demo or recorded backup?

---

## Where to Develop the Agent Code

### Recommended Project Structure

Create your agent code in the capstone folder alongside the ticketing system:

```
GAI-3101-CAP-1-GAI-3101-CAP-1764171407/
└── LabFiles/
    └── capstone/
        ├── ticketing-system/          # Existing - Node.js backend (DO NOT MODIFY)
        ├── support-info/              # Existing - RAG knowledge base (DO NOT MODIFY)
        ├── basic-ticket-agent.ipynb   # Existing - Starter code reference
        │
        ├── beanbotics_agent/          # 👈 CREATE THIS - Your Python agent package
        │   ├── __init__.py
        │   ├── agent.py               # Main LangGraph workflow definition
        │   ├── state.py               # State schema (TypedDict)
        │   ├── nodes/                 # Individual workflow nodes
        │   │   ├── __init__.py
        │   │   ├── fetch_tickets.py
        │   │   ├── classify.py
        │   │   ├── prioritize.py
        │   │   └── update_ticket.py
        │   ├── prompts/               # LLM prompts
        │   │   ├── classification.py
        │   │   └── priority.py
        │   └── rag/                   # RAG components (optional)
        │       ├── __init__.py
        │       └── retriever.py
        │
        ├── main.py                    # 👈 CREATE THIS - Entry point to run the agent
        ├── requirements.txt           # 👈 CREATE THIS - Python dependencies
        └── tests/                     # 👈 CREATE THIS - Test files
            └── test_classification.py
```

### Alternative: Single-File Approach

For a simpler approach, you can develop everything in a single Python file:

```
GAI-3101-CAP-1-GAI-3101-CAP-1764171407/
└── LabFiles/
    └── capstone/
        ├── ticketing-system/          # Existing
        ├── support-info/              # Existing
        ├── basic-ticket-agent.ipynb   # Existing reference
        │
        ├── beanbotics_agent.py        # 👈 CREATE THIS - All agent code in one file
        └── requirements.txt           # 👈 CREATE THIS - Python dependencies
```

### Using the Starter Notebook as a Base

You can also extend the existing `basic-ticket-agent.ipynb` notebook, but for a production-ready agent, a standalone Python file is recommended. The notebook contains working examples of:

1. **WebSocket connection** - See the `listen_for_ticket_updates()` function
2. **OpenAPI agent setup** - See the `planner.create_openapi_agent()` call
3. **RAG vector store** - See the `InMemoryVectorStore` example

### Key Code Patterns from Starter Resources

**From `basic-ticket-agent.ipynb`:**
```python
# API Integration
from langchain_community.agent_toolkits.openapi import planner
from langchain_community.utilities.requests import RequestsWrapper

agent = planner.create_openapi_agent(
    api_spec=openapi_spec,
    requests_wrapper=RequestsWrapper(),
    llm=ChatOpenAI(model_name="gpt-4o", temperature=0.0),
    allow_dangerous_requests=True,
    allow_operations=['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
)
```

**From `LangChain_LangGraph_Chatbot_Template.py`:**
```python
# State Management with LangGraph
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class AgentState(TypedDict):
    ticket_id: str
    category: str
    priority: str
    # ... add more fields

workflow = StateGraph(state_schema=AgentState)
workflow.add_node("classify", classify_ticket)
workflow.add_edge(START, "classify")
# ... build your graph
```

---

## Next Steps

**🎉 ALL FEATURES IMPLEMENTED!** The agent can now:
- Classify tickets into 8 categories
- Assign priority levels (High/Medium/Low)
- Extract or generate serial numbers
- Detect missing information and request it from customers
- Check escalation criteria and escalate to human agents when needed
- Use RAG to generate troubleshooting responses from support documentation
- Post all responses to tickets via API
- Run in batch mode or real-time WebSocket mode

### Completed
1. ~~Phase 1: Environment setup~~ → ✅ Complete
2. ~~Phase 2: Architecture design~~ → ✅ Complete
3. ~~Phase 3: MVP Implementation~~ → ✅ Complete
4. ~~Phase 4.1: Serial Number Extraction/Generation~~ → ✅ Complete
5. ~~Phase 4.2: Missing Information Handling~~ → ✅ Complete
6. ~~Phase 4.3: RAG System Integration~~ → ✅ Complete
7. ~~Phase 4.4: WebSocket Real-Time Mode~~ → ✅ Complete
8. ~~Phase 4.5: Escalation Logic~~ → ✅ Complete

### Current: Final Testing & Demo Preparation
1. Start the ticketing system: `cd ticketing-system && npm run dev`
2. Configure `secrets.env` with your OpenAI API key
3. Test batch mode: `python beanbotics_agent.py`
4. Test real-time mode: `python beanbotics_agent.py --watch`
5. Test escalation by creating a ticket mentioning "smoke" or "leak"
6. Test missing info by creating a very short ticket
7. Prepare presentation slides

### Running the Agent

**Batch Mode (process all unprocessed tickets once):**
```bash
python beanbotics_agent.py
```

**Real-Time Mode (WebSocket - continuously listen for new tickets):**
```bash
python beanbotics_agent.py --watch
```

---

*Plan created: December 2024*
*Updated: December 2024 - ALL FEATURES IMPLEMENTED*