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

## Phase 1: Environment Setup & Familiarization

### 1.1 Development Environment

- [ ] Set up Python virtual environment
- [ ] Install required dependencies:
  ```
  langchain==0.3.*
  langchain_openai==0.3.*
  langchain_community
  unstructured[md]==0.17.*
  langgraph==0.4.*
  websockets==15.0.*
  tiktoken
  ```
- [ ] Configure OpenAI API key in environment variables
- [ ] Test basic LangChain/LangGraph connectivity

### 1.2 Ticketing System Setup

- [ ] Navigate to `GAI-3101-CAP-1-GAI-3101-CAP-1764171407/LabFiles/capstone/ticketing-system/`
- [ ] Run `npm install` to install Node.js dependencies
- [ ] Start the ticketing system with `npm run dev`
- [ ] Access the UI at `http://localhost:3000` (or configured port)
- [ ] Review the Swagger documentation at `/api/docs`
- [ ] Familiarize with the OpenAPI spec at `/api/docs/openapi.json`

### 1.3 Review Existing Resources

- [ ] Study `basic-ticket-agent.ipynb` - the starter notebook with key patterns
- [ ] Study `LangChain_LangGraph_Chatbot_Template.py` - template for LangGraph workflows
- [ ] Review all 7 support documentation files in `support-info/` folder
- [ ] Examine sample tickets in `tickets.json` to understand data format

---

## Phase 2: Core Agent Architecture Design

### 2.1 Define Agent State Schema

Design a state structure to track:

- Current ticket being processed
- Extracted information (customer name, email, serial number, subject, description)
- Classification result (category)
- Priority level
- Missing information flags
- Processing status
- RAG context (if using documentation)

### 2.2 Define Classification Categories

Based on the support documentation, your categories should include:

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

## Phase 3: Core Feature Implementation

### 3.1 API Integration Layer

- [ ] Create OpenAPI agent using `create_openapi_agent()` from LangChain
- [ ] Load and reduce the OpenAPI spec using `reduce_openapi_spec()`
- [ ] Configure `RequestsWrapper` for API calls
- [ ] Implement ticket fetching (GET /api/tickets)
- [ ] Implement ticket updating (POST /api/tickets/:id)
- [ ] Implement response posting (POST /api/tickets/:id/responses)

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

### 3.3 Classification Engine

- [ ] Create classification prompt with clear category definitions
- [ ] Include few-shot examples for each category
- [ ] Use structured output to ensure consistent category assignment
- [ ] Handle edge cases and multi-category scenarios

### 3.4 Priority Assignment

- [ ] Create priority detection prompt
- [ ] Define urgency keywords/patterns for each level
- [ ] Consider category in priority (e.g., water leaks = high priority)
- [ ] Handle ambiguous cases with sensible defaults

### 3.5 Ticket Update Workflow

- [ ] Update ticket with extracted category
- [ ] Update ticket with assigned priority
- [ ] Update ticket status as appropriate
- [ ] Log all actions for audit trail

---

## Phase 4: Optional/Enhanced Features

### 4.1 Missing Information Handling

- [ ] Detect incomplete tickets (missing serial number, vague descriptions)
- [ ] Generate polite response requesting specific missing details
- [ ] Post response via API to ticket thread
- [ ] Track which tickets are awaiting customer response

### 4.2 RAG System Integration

- [ ] Load support documentation from `support-info/` using `DirectoryLoader`
- [ ] Create vector store using `InMemoryVectorStore` with OpenAI embeddings
- [ ] Implement semantic search for relevant documentation
- [ ] Generate suggested troubleshooting steps based on retrieved docs
- [ ] Include documentation-based suggestions in ticket responses

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

### 4.3 WebSocket Real-Time Integration

- [ ] Implement async WebSocket listener for real-time ticket updates
- [ ] Handle `ticket_created` events to process new tickets immediately
- [ ] Handle `ticket_updated` events if relevant
- [ ] Include fallback to HTTP polling if WebSocket unavailable

**WebSocket Events:**

- `ticket_created` - New ticket submitted
- `ticket_updated` - Ticket fields modified
- `ticket_deleted` - Ticket removed
- `response_added` - New response on ticket
- `status_changed` - Ticket status updated

### 4.4 Escalation Logic

- [ ] Define escalation criteria (complex issues, safety concerns, repeat complaints)
- [ ] Update ticket status to "escalated" when criteria met
- [ ] Generate escalation summary for human agents
- [ ] Tag with appropriate escalation team based on category

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

### Minimum Viable Product (MVP)

- [ ] Agent reads tickets from API
- [ ] Agent correctly classifies tickets into categories
- [ ] Agent assigns appropriate priority levels
- [ ] Agent updates tickets in the system

### Enhanced Version

- [ ] Agent requests missing information from customers
- [ ] Agent uses RAG to provide troubleshooting guidance
- [ ] Agent escalates complex issues appropriately
- [ ] Agent monitors real-time updates via WebSocket

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

## Next Steps

1. Schedule team meeting to review this plan
2. Assign roles and responsibilities
3. Set up shared development environment
4. Begin Phase 1 tasks
5. Create a shared task board (Trello, GitHub Projects, etc.) to track progress

---

*Plan created: December 2024*