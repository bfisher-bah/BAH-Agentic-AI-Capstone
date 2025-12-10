# Ticketing System

This directory contains a simple ticketing system designed for educational purposes. It demonstrates a basic architecture for handling support tickets, suitable for capstone projects or as a foundation for more advanced systems.

## Directory Structure

```
ticketing-system/
├── index.html         # Frontend HTML interface
├── index.js           # Main backend server logic (Node.js)
├── nodemon.json       # Nodemon configuration for development
├── package.json       # Node.js project metadata and dependencies
├── tickets.json       # Data store for tickets (JSON format)
```

## Architecture Overview

- **Frontend (index.html):**
  - Provides a user interface for submitting and viewing support tickets.
  - Communicates with the backend via HTTP requests (typically using fetch or AJAX).

- **Backend (index.js):**
  - Implements a simple Node.js server (often using Express.js) to handle API requests.
  - Routes include endpoints for creating, retrieving, and updating tickets.
  - Reads from and writes to `tickets.json` to persist ticket data.

- **Data Storage (tickets.json):**
  - Stores all ticket information in a flat JSON array.
  - Each ticket typically includes fields like `id`, `subject`, `description`, `status`, and timestamps.

- **Development Tools:**
  - `nodemon.json` configures automatic server restarts during development.
  - `package.json` lists dependencies (such as Express) and scripts for running the server.

---

For more details, see the code in each file and the comments within `index.js`.
