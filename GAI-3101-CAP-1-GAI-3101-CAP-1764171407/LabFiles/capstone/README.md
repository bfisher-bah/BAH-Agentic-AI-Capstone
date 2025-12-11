# BeanBotics Support Agent

An automated ticket classification and processing system for BeanBotics Inc., maker of the "Bean Machine" coffee robot.

## Overview

This agent automatically:
1. Fetches unprocessed tickets from the ticketing system API
2. Classifies tickets into categories (Mechanical, Coffee Quality, Maintenance, etc.)
3. Assigns priority levels (High, Medium, Low)
4. Extracts serial numbers from ticket descriptions
5. Updates tickets in the system via API

**This is NOT an interactive chatbot** - it's an autonomous processor that can run in batch mode (process once) or real-time mode (WebSocket listener).

## Project Structure

```
capstone/
├── ticketing-system/       # Node.js ticketing API (DO NOT MODIFY)
├── support-info/           # RAG knowledge base documents (DO NOT MODIFY)
├── basic-ticket-agent.ipynb # Reference notebook with examples
│
├── beanbotics_agent.py     # Main agent code
├── secrets.env.example     # Configuration template
├── secrets.env             # Your configuration (create this)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key

## Setup Instructions

### Step 1: Start the Ticketing System

```bash
# Navigate to the ticketing system folder
cd ticketing-system

# Install Node.js dependencies (first time only)
npm install

# Start the server
npm run dev
```

The ticketing system will be available at:
- **Web UI:** http://localhost:3000
- **API Docs:** http://localhost:3000/api/docs
- **OpenAPI Spec:** http://localhost:3000/api/docs/openapi.json

### Step 2: Configure the Agent

```bash
# Navigate back to capstone folder
cd ..

# Copy the example configuration
cp secrets.env.example secrets.env

# Edit secrets.env with your OpenAI API key
# Use your preferred text editor
```

**secrets.env contents:**
```
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o
TICKETING_API_URL=http://localhost:3000
```

### Step 3: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Run the Agent

```bash
python beanbotics_agent.py
```

## Usage

### Batch Mode (Default)

Process all unprocessed tickets once and exit:

```bash
python beanbotics_agent.py
```

### Real-Time Mode (WebSocket)

Continuously listen for new tickets and process them as they arrive:

```bash
python beanbotics_agent.py --watch
```

### Show Help

```bash
python beanbotics_agent.py --help
```

### From Jupyter/SageMaker

```python
# Batch mode
import os
os.environ["OPENAI_API_KEY"] = "sk-your-key-here"

from beanbotics_agent import run_agent
run_agent()

# Real-time mode (async)
from beanbotics_agent import run_agent_websocket
await run_agent_websocket()
```

## Expected Output

### Batch Mode

```
============================================================
BeanBotics Support Agent - Batch Mode
============================================================
API URL: http://localhost:3000
Model: gpt-4o
============================================================

------------------------------------------------------------
PROCESSING LOG:
------------------------------------------------------------
[FETCH] Fetching tickets from API...
[FETCH] Found 4 total tickets, 2 need processing

[SELECT] Processing ticket 1/2: abc-123...
[SELECT] Subject: Machine not grinding beans
[CLASSIFY] Analyzing ticket content...
[CLASSIFY] Category: Mechanical
[PRIORITY] Determining priority level...
[PRIORITY] Priority: High
[SERIAL] Extracted serial number: BM-1001
[UPDATE] Updating ticket abc-123...
[UPDATE] Success! category='Mechanical', priority='High', serial_number='BM-1001'

============================================================
Agent finished.
============================================================
```

### Real-Time Mode

```
============================================================
BeanBotics Support Agent - Real-Time Mode
============================================================
API URL: http://localhost:3000
WebSocket URL: ws://localhost:3000/ws
Model: gpt-4o
============================================================

Listening for new tickets... (Press Ctrl+C to stop)
------------------------------------------------------------
[CONNECTED] WebSocket connection established

[EVENT] created: abc-123

[WEBSOCKET] Processing new ticket: abc-123
[CLASSIFY] Analyzing ticket content...
[CLASSIFY] Category: Mechanical
[PRIORITY] Determining priority level...
[PRIORITY] Priority: High
[SERIAL] No serial number found in ticket text
[UPDATE] Success! category='Mechanical', priority='High'
```

## Classification Categories

| Category | Description |
|----------|-------------|
| Mechanical | Machine not grinding, motors, physical issues |
| Coffee Quality | Taste issues, consistency problems |
| Maintenance | Cleaning cycles, drip tray, descaling, leaks |
| Technical | Software updates, connectivity, errors |
| Power/Startup | Machine won't turn on, power issues |
| Installation/Setup | Initial setup, registration, calibration |
| Feature Request | Customer suggestions for new features |
| General Inquiry | Warranty, training, documentation questions |

## Priority Levels

| Priority | Criteria |
|----------|----------|
| High | Safety concerns, machine completely down, water leak, urgent language |
| Medium | Partial functionality issues, quality concerns, general problems |
| Low | Feature requests, general inquiries, non-urgent questions |

## API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/tickets` | Fetch all tickets |
| POST | `/api/tickets/{id}` | Update ticket category/priority |

## Troubleshooting

### "Connection refused" error
- Make sure the ticketing system is running (`npm run dev` in ticketing-system folder)
- Verify the URL in secrets.env matches where the server is running

### "Invalid API key" error
- Check that your OpenAI API key is correct in secrets.env
- Ensure there are no extra spaces or quotes around the key

### "No tickets to process"
- All tickets already have category and priority assigned
- Create a new ticket in the web UI (http://localhost:3000) without filling in category/priority

## Features

### Implemented
- [x] Batch mode - process all unprocessed tickets once
- [x] Real-time mode - WebSocket listener for continuous processing (`--watch` flag)
- [x] Automatic classification into 8 categories
- [x] Priority assignment (High/Medium/Low)
- [x] Serial number extraction from ticket text
- [x] Auto-reconnect on WebSocket disconnection

### Future Enhancements
- [ ] RAG integration for automated troubleshooting responses
- [ ] Missing information detection
- [ ] Escalation logic for complex issues