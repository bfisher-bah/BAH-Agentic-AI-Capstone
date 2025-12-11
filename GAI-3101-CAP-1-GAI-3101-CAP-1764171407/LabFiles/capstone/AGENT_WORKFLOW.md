# BeanBotics Support Agent - Workflow Documentation

## Overview

The BeanBotics Support Agent is an automated ticket processing system built with LangGraph. It processes support tickets through a series of nodes that classify, prioritize, and respond to customer issues.

## LangGraph Workflow

```mermaid
graph TD
    START((START)) --> fetch_tickets

    fetch_tickets[Fetch Tickets] --> select_next[Select Next Ticket]

    select_next --> |"process_next"| classify[Classify Ticket]
    select_next --> |"done"| END((END))

    classify --> prioritize[Assign Priority]
    prioritize --> extract_serial[Extract Serial Number]
    extract_serial --> check_escalation[Check Escalation]
    check_escalation --> handle_escalation[Handle Escalation]
    handle_escalation --> detect_missing_info[Detect Missing Info]
    detect_missing_info --> request_missing_info[Request Missing Info]
    request_missing_info --> generate_response[Generate RAG Response]
    generate_response --> post_response[Post Response]
    post_response --> update[Update Ticket]
    update --> increment[Increment Index]
    increment --> select_next

    style START fill:#22c55e,color:#fff
    style END fill:#ef4444,color:#fff
    style classify fill:#3b82f6,color:#fff
    style prioritize fill:#3b82f6,color:#fff
    style check_escalation fill:#f59e0b,color:#fff
    style handle_escalation fill:#f59e0b,color:#fff
    style generate_response fill:#8b5cf6,color:#fff
```

## Node Descriptions

### 1. Fetch Tickets
- **Purpose**: Retrieve unprocessed tickets from the ticketing system API
- **Logic**:
  - If tickets are pre-loaded in state (e.g., for re-processing after customer response), use those
  - Otherwise, fetch all tickets and filter for unprocessed ones (missing category or priority)

### 2. Select Next Ticket
- **Purpose**: Pick the next ticket from the queue for processing
- **Routing**:
  - `process_next` - Continue to classification if tickets remain
  - `done` - End workflow if no more tickets

### 3. Classify Ticket
- **Purpose**: Use LLM to categorize the ticket
- **Categories**:
  - Mechanical
  - Coffee Quality
  - Maintenance
  - Technical
  - Power/Startup
  - Installation/Setup
  - Feature Request
  - General Inquiry

### 4. Assign Priority
- **Purpose**: Use LLM to determine urgency level
- **Priority Levels**:
  - **High**: Safety concerns, machine non-functional, water leaks, urgent language
  - **Medium**: Partial functionality, quality concerns, general problems
  - **Low**: Feature requests, general inquiries, non-urgent questions

### 5. Extract Serial Number
- **Purpose**: Find or generate a serial number for the ticket
- **Logic**:
  - Extract from ticket text using regex patterns (BM-1001, S/N:, etc.)
  - Generate deterministic serial if none found

### 6. Check Escalation
- **Purpose**: Determine if human intervention is needed
- **Escalation Triggers**:
  - Safety keywords: smoke, burning, fire, spark, shock, electric, danger
  - Water leak or water damage
  - High priority Mechanical/Power issues
  - Customer frustration indicators
  - Recurring/repeated issues

### 7. Handle Escalation
- **Purpose**: Process escalated tickets
- **Actions**:
  - Post escalation notice to ticket
  - Update ticket status to "escalated"
  - Provide emergency hotline information

### 8. Detect Missing Info
- **Purpose**: Check if critical information is missing
- **Checks**:
  - Serial number presence
  - Description length (minimum 20 characters)
  - Category-specific requirements (bean type for Coffee Quality, lights for Power/Startup, etc.)

### 9. Request Missing Info
- **Purpose**: Post a polite request for additional information
- **Output**: Formatted message listing missing items

### 10. Generate RAG Response
- **Purpose**: Create helpful troubleshooting response using documentation
- **Process**:
  - Query vector store with ticket content
  - Retrieve top 3 relevant documents
  - Generate contextual response with LLM

### 11. Post Response
- **Purpose**: Submit the generated response to the ticket

### 12. Update Ticket
- **Purpose**: Save classification results to the API
- **Fields Updated**: category, priority, serial_number

### 13. Increment Index
- **Purpose**: Move to the next ticket in the queue

---

## Processing Modes

### Batch Mode
Process all unprocessed tickets once and exit.

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant API
    participant LLM
    participant RAG

    User->>Agent: python beanbotics_agent.py
    Agent->>API: GET /api/tickets
    API-->>Agent: All tickets

    loop For each unprocessed ticket
        Agent->>LLM: Classify ticket
        LLM-->>Agent: Category
        Agent->>LLM: Assign priority
        LLM-->>Agent: Priority
        Agent->>Agent: Check escalation

        alt Needs escalation
            Agent->>API: POST escalation message
            Agent->>API: POST status=escalated
        end

        Agent->>RAG: Query documentation
        RAG-->>Agent: Relevant docs
        Agent->>LLM: Generate response
        LLM-->>Agent: Troubleshooting steps
        Agent->>API: POST response
        Agent->>API: POST ticket update
    end

    Agent-->>User: Processing complete
```

### WebSocket Real-Time Mode
Continuously listen for new tickets and customer responses.

```mermaid
sequenceDiagram
    participant Customer
    participant TicketSystem
    participant WebSocket
    participant Agent
    participant LLM

    Agent->>WebSocket: Connect to /ws
    WebSocket-->>Agent: Connected

    Customer->>TicketSystem: Create ticket
    TicketSystem->>WebSocket: Event: created
    WebSocket->>Agent: {ticketId, updateType: "created"}
    Agent->>Agent: process_single_ticket()
    Note over Agent: Full workflow execution

    Customer->>TicketSystem: Add response
    TicketSystem->>WebSocket: Event: response
    WebSocket->>Agent: {ticketId, updateType: "response"}
    Agent->>Agent: process_customer_response()
    Note over Agent: Combine description + response
    Note over Agent: Re-run full workflow
    Note over Agent: Check for escalation triggers
```

---

## Customer Response Re-Processing Flow

When a customer responds with new information, the agent re-evaluates the ticket:

```mermaid
flowchart TD
    A[Customer Response Event] --> B{Already Escalated?}
    B -->|Yes| C[Skip Processing]
    B -->|No| D{Response from Customer?}
    D -->|No| C
    D -->|Yes| E[Combine Original + New Info]
    E --> F[Clear Category/Priority]
    F --> G[Run Full Workflow]
    G --> H{Escalation Needed?}
    H -->|Yes| I[Escalate Ticket]
    H -->|No| J[Generate Follow-up Response]
    I --> K[Update Status]
    J --> K
    K --> L[Done]

    style A fill:#22c55e,color:#fff
    style I fill:#ef4444,color:#fff
    style J fill:#8b5cf6,color:#fff
```

---

## Escalation Decision Flow

```mermaid
flowchart TD
    A[Check Escalation] --> B{Safety Keywords?}
    B -->|smoke, burning, fire, spark, shock| YES[ESCALATE]
    B -->|No| C{Water Leak?}
    C -->|Yes| YES
    C -->|No| D{High Priority + Mechanical/Power?}
    D -->|Yes| YES
    D -->|No| E{Frustration Keywords?}
    E -->|furious, angry, lawsuit, refund| YES
    E -->|No| F{Recurring Issue?}
    F -->|Yes| YES
    F -->|No| NO[No Escalation]

    YES --> G[Post Escalation Notice]
    G --> H[Set Status = escalated]
    H --> I[Provide Hotline Info]

    style YES fill:#ef4444,color:#fff
    style NO fill:#22c55e,color:#fff
```

---

## RAG System Architecture

```mermaid
flowchart LR
    subgraph Documents
        D1[machine-wont-start.md]
        D2[software-update.md]
        D3[coffee-quality.md]
        D4[cleaning-maintenance.md]
        D5[installation-setup.md]
        D6[feature-request.md]
        D7[general-inquiry.md]
    end

    subgraph RAG Pipeline
        Documents --> Loader[DirectoryLoader]
        Loader --> Embeddings[OpenAI Embeddings]
        Embeddings --> VectorStore[InMemoryVectorStore]
        VectorStore --> Retriever
    end

    subgraph Query Flow
        Ticket[Ticket Content] --> Query[Build Query]
        Query --> Retriever
        Retriever --> TopDocs[Top 3 Documents]
        TopDocs --> LLM[Generate Response]
        LLM --> Response[Troubleshooting Steps]
    end

    style VectorStore fill:#8b5cf6,color:#fff
    style LLM fill:#3b82f6,color:#fff
```

---

## Configuration

### Environment Variables (secrets.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | OpenAI API key for LLM and embeddings |
| `OPENAI_MODEL` | `gpt-4o` | Model to use for classification and responses |
| `TICKETING_API_URL` | `http://localhost:3000` | Ticketing system base URL |

### Running the Agent

```bash
# Batch mode - process all unprocessed tickets once
python beanbotics_agent.py

# Real-time mode - listen for new tickets via WebSocket
python beanbotics_agent.py --watch

# Show help
python beanbotics_agent.py --help
```

---

## API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/tickets` | List all tickets |
| GET | `/api/tickets/:id` | Get ticket with responses |
| POST | `/api/tickets/:id` | Update ticket fields |
| POST | `/api/tickets/:id/responses` | Add response to ticket |
| POST | `/api/tickets/:id/status` | Update ticket status |
| WS | `/ws` | WebSocket for real-time events |