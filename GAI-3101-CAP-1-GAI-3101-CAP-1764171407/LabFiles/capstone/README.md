# BeanBotics Support Agent

An automated ticket classification and processing system for BeanBotics Inc., maker of the "Bean Machine" coffee robot.

## Overview

This agent automatically:
1. Fetches unprocessed tickets from the ticketing system API
2. Classifies tickets into categories (Mechanical, Coffee Quality, Maintenance, etc.)
3. Assigns priority levels (High, Medium, Low)
4. Updates tickets in the system via API

**This is NOT an interactive chatbot** - it's an autonomous batch processor that runs, processes tickets, and exits.

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

### Command Line

```bash
python beanbotics_agent.py
```

### From Jupyter/SageMaker

```python
# Option 1: Set environment variable first
import os
os.environ["OPENAI_API_KEY"] = "sk-your-key-here"

from beanbotics_agent import run_agent
run_agent()

# Option 2: Load from secrets.env (if in same directory)
from beanbotics_agent import run_agent
run_agent()
```

## Expected Output

```
============================================================
BeanBotics Support Agent - MVP
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
[UPDATE] Updating ticket abc-123...
[UPDATE] Success! Ticket updated with category='Mechanical', priority='High'

[SELECT] Processing ticket 2/2: def-456...
...

============================================================
Agent finished.
============================================================
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

## Next Steps (Future Enhancements)

- [ ] WebSocket listener for real-time processing
- [ ] RAG integration for automated troubleshooting responses
- [ ] Missing information detection
- [ ] Escalation logic for complex issues