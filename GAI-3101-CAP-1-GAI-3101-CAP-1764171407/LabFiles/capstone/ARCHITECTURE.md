# BeanBotics Support Agent - Architecture Documentation

## System Architecture Overview

```mermaid
flowchart TB
    subgraph Client["Client Layer"]
        UI[Web UI<br/>localhost:3000]
        CLI[CLI Agent<br/>beanbotics_agent.py]
    end

    subgraph TicketingSystem["Ticketing System (Node.js)"]
        API[REST API<br/>/api/tickets/*]
        WS[WebSocket Server<br/>/ws]
        DB[(tickets.json<br/>File Storage)]
    end

    subgraph Agent["BeanBotics Agent (Python)"]
        direction TB
        LG[LangGraph<br/>State Machine]

        subgraph Nodes["Workflow Nodes"]
            N1[Fetch]
            N2[Classify]
            N3[Prioritize]
            N4[Escalate]
            N5[RAG Response]
            N6[Update]
        end
    end

    subgraph External["External Services"]
        OpenAI[OpenAI API<br/>gpt-4o]
    end

    subgraph RAG["RAG System"]
        Docs[Support Docs<br/>support-info/*.md]
        Embed[OpenAI Embeddings]
        VS[InMemory<br/>VectorStore]
    end

    UI -->|Create/View Tickets| API
    CLI -->|Batch Processing| API
    CLI <-->|Real-time Events| WS

    API <--> DB
    WS <--> DB

    LG --> Nodes
    N2 -->|Classification| OpenAI
    N3 -->|Priority| OpenAI
    N5 -->|Response Gen| OpenAI

    Docs --> Embed
    Embed --> VS
    VS -->|Retrieval| N5

    N1 -->|GET| API
    N6 -->|POST| API

    style UI fill:#22c55e,color:#fff
    style CLI fill:#22c55e,color:#fff
    style API fill:#3b82f6,color:#fff
    style WS fill:#3b82f6,color:#fff
    style LG fill:#8b5cf6,color:#fff
    style OpenAI fill:#f59e0b,color:#fff
    style VS fill:#ec4899,color:#fff
```

---

## Component Architecture

```mermaid
flowchart LR
    subgraph PythonAgent["Python Agent (beanbotics_agent.py)"]
        direction TB

        subgraph Core["Core Components"]
            Config[Configuration<br/>secrets.env]
            State[AgentState<br/>TypedDict]
            LLM[ChatOpenAI<br/>LLM Client]
        end

        subgraph Workflow["LangGraph Workflow"]
            Builder[StateGraph<br/>Builder]
            Nodes[Workflow<br/>Nodes]
            Router[Conditional<br/>Routing]
        end

        subgraph RAGSystem["RAG System"]
            Loader[DirectoryLoader]
            Embeddings[OpenAIEmbeddings]
            VectorStore[InMemoryVectorStore]
            Retriever[Retriever]
        end

        subgraph Modes["Execution Modes"]
            Batch[run_agent<br/>Batch Mode]
            WebSocket[run_agent_websocket<br/>Real-time Mode]
        end
    end

    Config --> LLM
    Config --> Embeddings
    State --> Builder
    Nodes --> Builder
    Router --> Builder
    Loader --> VectorStore
    Embeddings --> VectorStore
    VectorStore --> Retriever
    Builder --> Batch
    Builder --> WebSocket

    style Config fill:#6b7280,color:#fff
    style LLM fill:#f59e0b,color:#fff
    style Builder fill:#8b5cf6,color:#fff
    style VectorStore fill:#ec4899,color:#fff
    style Batch fill:#22c55e,color:#fff
    style WebSocket fill:#22c55e,color:#fff
```

---

## Data Flow Architecture

```mermaid
flowchart LR
    subgraph Input["Input Sources"]
        NewTicket[New Ticket<br/>via UI]
        CustomerReply[Customer<br/>Response]
        BatchRun[Batch<br/>Trigger]
    end

    subgraph Processing["Agent Processing"]
        direction TB
        Fetch[Fetch/Load<br/>Ticket]
        Enrich[Enrich with<br/>Customer Response]
        Classify[LLM<br/>Classification]
        Priority[LLM<br/>Prioritization]
        Escalation[Escalation<br/>Check]
        RAG[RAG<br/>Retrieval]
        Response[LLM Response<br/>Generation]
    end

    subgraph Output["Output Actions"]
        UpdateTicket[Update Ticket<br/>Category/Priority]
        PostResponse[Post Agent<br/>Response]
        EscalateTicket[Escalate &<br/>Notify]
        RequestInfo[Request<br/>Missing Info]
    end

    subgraph Storage["Data Storage"]
        TicketDB[(Ticket<br/>Database)]
        SupportDocs[(Support<br/>Documentation)]
    end

    NewTicket --> Fetch
    CustomerReply --> Enrich
    BatchRun --> Fetch
    Enrich --> Fetch

    Fetch --> Classify
    Classify --> Priority
    Priority --> Escalation

    Escalation -->|Needs Escalation| EscalateTicket
    Escalation -->|No Escalation| RAG

    SupportDocs --> RAG
    RAG --> Response

    Response --> PostResponse
    Response -->|Missing Info| RequestInfo
    Classify --> UpdateTicket
    Priority --> UpdateTicket

    UpdateTicket --> TicketDB
    PostResponse --> TicketDB
    EscalateTicket --> TicketDB

    style NewTicket fill:#22c55e,color:#fff
    style CustomerReply fill:#22c55e,color:#fff
    style Classify fill:#3b82f6,color:#fff
    style Priority fill:#3b82f6,color:#fff
    style RAG fill:#ec4899,color:#fff
    style EscalateTicket fill:#ef4444,color:#fff
```

---

## Technology Stack

```mermaid
flowchart TB
    subgraph Frontend["Frontend"]
        HTML[HTML/CSS/JS]
        WebUI[Ticket Management UI]
    end

    subgraph Backend["Backend - Ticketing System"]
        NodeJS[Node.js]
        Express[Express.js]
        WSLib[ws Library]
        Swagger[Swagger/OpenAPI]
    end

    subgraph AgentStack["Agent Stack"]
        Python[Python 3.x]
        LangChain[LangChain]
        LangGraph[LangGraph]
        OpenAILib[langchain-openai]
    end

    subgraph AI["AI/ML Services"]
        GPT4[GPT-4o<br/>Classification & Generation]
        EmbedAPI[text-embedding-ada-002<br/>Document Embeddings]
    end

    subgraph DataStores["Data Stores"]
        JSON[(tickets.json)]
        MemStore[(InMemoryVectorStore)]
        MDFiles[(Markdown Files)]
    end

    HTML --> WebUI
    WebUI --> Express
    NodeJS --> Express
    Express --> WSLib
    Express --> Swagger
    Express --> JSON

    Python --> LangChain
    LangChain --> LangGraph
    LangChain --> OpenAILib
    OpenAILib --> GPT4
    OpenAILib --> EmbedAPI

    MDFiles --> MemStore
    EmbedAPI --> MemStore

    style Python fill:#3776ab,color:#fff
    style NodeJS fill:#339933,color:#fff
    style GPT4 fill:#f59e0b,color:#fff
    style LangGraph fill:#8b5cf6,color:#fff
```

---

## Deployment Architecture

```mermaid
flowchart TB
    subgraph Local["Local Development Environment"]
        subgraph TicketServer["Ticketing Server"]
            Node[Node.js Process<br/>Port 3000]
        end

        subgraph AgentProcess["Agent Process"]
            Py[Python Process<br/>beanbotics_agent.py]
        end

        subgraph Files["File System"]
            Tickets[tickets.json]
            Secrets[secrets.env]
            Support[support-info/]
        end
    end

    subgraph Cloud["Cloud Services"]
        OpenAICloud[OpenAI API<br/>api.openai.com]
    end

    Node <-->|HTTP/WS| Py
    Node <--> Tickets
    Py --> Secrets
    Py --> Support
    Py <-->|HTTPS| OpenAICloud

    style Node fill:#339933,color:#fff
    style Py fill:#3776ab,color:#fff
    style OpenAICloud fill:#f59e0b,color:#fff
```

---

## State Management

```mermaid
flowchart LR
    subgraph AgentState["AgentState (TypedDict)"]
        direction TB

        subgraph TicketQueue["Ticket Queue"]
            tickets[tickets: List]
            index[current_index: int]
            current[current_ticket: dict]
        end

        subgraph Classification["Classification Results"]
            category[classified_category: str]
            priority[assigned_priority: str]
            serial[extracted_serial: str]
        end

        subgraph Escalation["Escalation State"]
            needs[needs_escalation: bool]
            reason[escalation_reason: str]
        end

        subgraph Response["Response State"]
            rag[rag_response: str]
            missing[missing_info: List]
        end

        subgraph Logging["Logging"]
            log[log: List]
            errors[errors: List]
        end
    end

    Start((Input)) --> tickets
    tickets --> index
    index --> current
    current --> category
    category --> priority
    priority --> serial
    serial --> needs
    needs --> reason
    reason --> rag
    rag --> missing
    missing --> log
    log --> errors
    errors --> End((Output))

    style tickets fill:#22c55e,color:#fff
    style category fill:#3b82f6,color:#fff
    style priority fill:#3b82f6,color:#fff
    style needs fill:#f59e0b,color:#fff
    style rag fill:#8b5cf6,color:#fff
```

---

## API Integration

```mermaid
sequenceDiagram
    participant Agent as BeanBotics Agent
    participant API as Ticketing API
    participant DB as tickets.json

    Note over Agent,DB: Fetch Tickets
    Agent->>API: GET /api/tickets
    API->>DB: Read all tickets
    DB-->>API: Ticket array
    API-->>Agent: JSON response

    Note over Agent,DB: Update Ticket
    Agent->>API: POST /api/tickets/:id
    API->>DB: Update ticket fields
    DB-->>API: Success
    API-->>Agent: Updated ticket

    Note over Agent,DB: Post Response
    Agent->>API: POST /api/tickets/:id/responses
    API->>DB: Add response to ticket
    DB-->>API: Success
    API-->>Agent: Response added

    Note over Agent,DB: Update Status
    Agent->>API: POST /api/tickets/:id/status
    API->>DB: Update status field
    DB-->>API: Success
    API-->>Agent: Status updated
```

---

## WebSocket Event Flow

```mermaid
sequenceDiagram
    participant UI as Web UI
    participant WS as WebSocket Server
    participant Agent as BeanBotics Agent

    Agent->>WS: Connect to /ws
    WS-->>Agent: Connection established

    UI->>WS: Create new ticket
    WS->>Agent: {"updateType": "created", "ticketId": "..."}
    Agent->>Agent: process_single_ticket()

    UI->>WS: Add response to ticket
    WS->>Agent: {"updateType": "response", "ticketId": "..."}
    Agent->>Agent: process_customer_response()

    UI->>WS: Update ticket
    WS->>Agent: {"updateType": "updated", "ticketId": "..."}
    Agent->>Agent: Skip (not handled)

    Note over Agent: Auto-reconnect on disconnect
    WS--xAgent: Connection lost
    Agent->>Agent: Wait 5 seconds
    Agent->>WS: Reconnect
```

---

## Security Considerations

```mermaid
flowchart TB
    subgraph Secrets["Sensitive Data"]
        APIKey[OpenAI API Key]
        Config[Configuration]
    end

    subgraph Protection["Protection Measures"]
        EnvFile[secrets.env<br/>Not in Git]
        GitIgnore[.gitignore]
        LocalOnly[Local Storage Only]
    end

    subgraph Network["Network Security"]
        HTTPS[HTTPS to OpenAI]
        LocalAPI[Localhost Only<br/>for Ticketing API]
    end

    APIKey --> EnvFile
    Config --> EnvFile
    EnvFile --> GitIgnore

    APIKey --> HTTPS
    LocalAPI --> LocalOnly

    style APIKey fill:#ef4444,color:#fff
    style EnvFile fill:#22c55e,color:#fff
    style HTTPS fill:#22c55e,color:#fff
```

---

## File Structure

```
capstone/
├── beanbotics_agent.py      # Main agent implementation
├── secrets.env              # Configuration (API keys)
├── AGENT_WORKFLOW.md        # Workflow documentation
├── ARCHITECTURE.md          # This file
│
├── support-info/            # RAG knowledge base
│   ├── machine-wont-start.md
│   ├── software-update.md
│   ├── coffee-quality.md
│   ├── cleaning-maintenance.md
│   ├── installation-setup.md
│   ├── feature-request.md
│   └── general-inquiry.md
│
└── ticketing-system/        # Node.js backend
    ├── index.js             # Express server
    ├── tickets.json         # Ticket storage
    ├── package.json
    └── public/              # Web UI
```