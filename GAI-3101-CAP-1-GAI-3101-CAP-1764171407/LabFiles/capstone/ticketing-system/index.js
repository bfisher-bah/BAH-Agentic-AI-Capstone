// Ticketing System API Server
// -----------------------------------
// This file implements a simple ticketing system backend using Node.js, Express, and lowdb.
// It provides RESTful API endpoints for managing support tickets, including creation, updates, responses, and status changes.
// WebSocket support is included for real-time ticket updates.

import express from 'express'; // Web framework for Node.js
import cors from 'cors'; // Middleware to enable Cross-Origin Resource Sharing
import { v4 as uuidv4 } from 'uuid'; // For generating unique ticket IDs
import { Low } from 'lowdb'; // Lowdb for simple JSON-based database
import { JSONFile } from 'lowdb/node'; // JSON file adapter for lowdb
import swaggerUi from 'swagger-ui-express'; // Swagger UI for API docs
import swaggerJSDoc from 'swagger-jsdoc'; // Swagger JSDoc for OpenAPI spec
import path from 'path'; // Node.js path utilities
import { fileURLToPath } from 'url'; // For ES module __dirname emulation
import Joi from 'joi'; // Data validation library
import { WebSocketServer } from 'ws'; // WebSocket server for real-time updates

const PORT = process.env.PORT || 3000; // Server port

const app = express();
app.use(cors()); // Enable CORS for all routes
app.use(express.json()); // Parse JSON request bodies

// Lowdb setup: tickets and responses are stored in tickets.json
const db = new Low(new JSONFile('tickets.json'), { tickets: [], responses: [] });

// Initialize database
await db.read();
if (!db.data) {
  db.data = { tickets: [], responses: [] };
  await db.write();
}

// Swagger setup for API documentation
const swaggerDefinition = {
  openapi: '3.0.0',
  info: {
    title: 'Bean Machine Ticketing System API',
    version: '1.0.0',
  },
};
const options = {
  swaggerDefinition,
  apis: ['./index.js'],
};
const swaggerSpec = swaggerJSDoc(options);

// Serve the raw OpenAPI JSON schema
app.get('/api/docs/openapi.json', (req, res) => {
  res.json(swaggerSpec);
});

// Serve Swagger UI for API documentation
app.use('/api/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

/**
 * @swagger
 * components:
 *   schemas:
 *     Ticket:
 *       type: object
 *       properties:
 *         id: { type: string }
 *         created_at: { type: string }
 *         customer_name: { type: string }
 *         customer_email: { type: string }
 *         subject: { type: string }
 *         serial_number: { type: string }
 *         description: { type: string }
 *         category: { type: string }
 *         priority: { type: string }
 *         status: { type: string }
 *     Response:
 *       type: object
 *       properties:
 *         id: { type: string }
 *         ticket_id: { type: string }
 *         author: { type: string }
 *         message: { type: string }
 *         created_at: { type: string }
 */

// -------------------
// Ticket Endpoints
// -------------------

/**
 * GET /api/tickets
 * Returns all tickets in the system.
 *
 * Reads the tickets array from the database and returns it as JSON.
 * No authentication or filtering is applied.
 */
app.get('/api/tickets', async (req, res) => {

  // Read the latest tickets from the database file
  await db.read();

  // Return all tickets as a JSON array
  res.json(db.data.tickets);
});

/**
 * POST /api/tickets
 * Creates a new ticket with validated fields.
 *
 * Validates the request body using Joi schema. If valid, generates a new ticket object
 * with a unique ID and timestamp, adds it to the database, writes to disk, and notifies
 * WebSocket clients of the new ticket. Returns the created ticket as JSON.
 *
 * Returns 400 if validation fails.
 */
app.post('/api/tickets', async (req, res) => {

  // Define allowed status values
  const allowedStatuses = ['open', 'in progress', 'closed', 'escalated'];

  // Validate the incoming request body using Joi
  const schema = Joi.object({
    customer_name: Joi.string().min(1).required(),
    customer_email: Joi.string().email().required(),
    subject: Joi.string().min(1).required(),
    description: Joi.string().min(1).required(),
    serial_number: Joi.string().allow(''),
    category: Joi.string().allow(''),
    priority: Joi.string().allow(''),
    status: Joi.string().valid(...allowedStatuses).optional()
  });
  const { error, value } = schema.validate(req.body);

  // If validation fails, return a 400 error
  if (error) return res.status(400).json({ error: error.details[0].message });

  // Default status to 'open' if not provided
  let status = (value.status || 'open').toLowerCase();

  // Construct the new ticket object
  const ticket = {
    id: uuidv4(),
    created_at: new Date().toISOString(),
    customer_name: value.customer_name,
    customer_email: value.customer_email,
    subject: value.subject,
    serial_number: value.serial_number || '',
    description: value.description,
    category: value.category || '',
    priority: value.priority || '',
    status
  };

  // Add the new ticket to the database
  db.data.tickets.push(ticket);

  // Persist the change to disk
  await db.write();

  // Notify WebSocket clients of the new ticket
  notifyTicketUpdate(ticket.id, 'created');

  // Return the created ticket
  res.status(201).json(ticket);
});

/**
 * @swagger
 * /api/tickets/{ticket_id}:
 *   get:
 *     summary: Get a ticket by ID
 *     parameters:
 *       - in: path
 *         name: ticket_id
 *         schema:
 *           type: string
 *         required: true
 *         description: Ticket ID
 *     responses:
 *       200:
 *         description: Ticket details (with responses)
 *         content:
 *           application/json:
 *             schema:
 *               allOf:
 *                 - $ref: '#/components/schemas/Ticket'
 *                 - type: object
 *                   properties:
 *                     responses:
 *                       type: array
 *                       items:
 *                         $ref: '#/components/schemas/Response'
 *       404:
 *         description: Ticket not found
 *   post:
 *     summary: Update any field of a ticket
 *     description: |
 *       Update one or more fields of an existing ticket. You can update the following fields: subject, description, category, priority, status, customer_name, customer_email, and serial_number. Use this endpoint to correct ticket details, reclassify, or change status/priority as the ticket progresses. Do not use this endpoint to add responses or comments—use the responses endpoint for that purpose.
 *       
 *       **Fields that can be updated:**
 *         - subject
 *         - description
 *         - category
 *         - priority
 *         - status
 *         - customer_name
 *         - customer_email
 *         - serial_number
 *       
 *       **When to use this endpoint:**
 *         - To correct or update ticket details (e.g., typo in subject, wrong email)
 *         - To reclassify a ticket (change category or priority)
 *         - To update the status as the ticket progresses (e.g., open → in progress)
 *         - To update customer information if needed
 *       
 *       **Do NOT use this endpoint to add responses or comments.** Use the /responses endpoint for that purpose.
 *     parameters:
 *       - in: path
 *         name: ticket_id
 *         schema:
 *           type: string
 *         required: true
 *         description: Ticket ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *     responses:
 *       200:
 *         description: Ticket updated
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Ticket'
 *       404:
 *         description: Ticket not found
 *   delete:
 *     summary: Delete a ticket
 *     parameters:
 *       - in: path
 *         name: ticket_id
 *         schema:
 *           type: string
 *         required: true
 *         description: Ticket ID
 *     responses:
 *       204:
 *         description: Ticket deleted
 *       404:
 *         description: Ticket not found
 */
app.get('/api/tickets/:ticket_id', async (req, res) => {

  // Read the latest data from the database
  await db.read();

  // Find the ticket with the given ID
  const ticket = db.data.tickets.find(t => t.id === req.params.ticket_id);

  // If not found, return 404
  if (!ticket) return res.status(404).json({ error: 'Ticket not found' });

  // Ensure responses array exists
  if (!db.data.responses) db.data.responses = [];

  // Filter responses for this ticket
  const responses = db.data.responses.filter(r => r.ticket_id === req.params.ticket_id);

  // Return the ticket with its responses
  res.json({ ...ticket, responses });
});

app.post('/api/tickets/:ticket_id', async (req, res) => {

  // Read the latest data from the database
  await db.read();

  // Find the ticket to update
  const ticket = db.data.tickets.find(t => t.id === req.params.ticket_id);

  // If not found, return 404
  if (!ticket) return res.status(404).json({ error: 'Ticket not found' });

  // Define allowed status values
  const allowedStatuses = ['open', 'in progress', 'closed', 'escalated'];

  // Validate the updatable fields
  const schema = Joi.object({
    customer_name: Joi.string().min(1),
    customer_email: Joi.string().email(),
    subject: Joi.string().min(1),
    description: Joi.string().min(1),
    serial_number: Joi.string().allow(''),
    category: Joi.string().allow(''),
    priority: Joi.string().allow(''),
    status: Joi.string().valid(...allowedStatuses)
  });
  const { error, value } = schema.validate(req.body);

  // If validation fails, return 400
  if (error) return res.status(400).json({ error: error.details[0].message });

  // Update the ticket with validated fields
  Object.assign(ticket, value);

  // Persist the change to disk
  await db.write();

  // Notify WebSocket clients of the update
  notifyTicketUpdate(ticket.id, 'updated');

  // Return the updated ticket
  res.json(ticket);
});

app.delete('/api/tickets/:ticket_id', async (req, res) => {

  // Read the latest data from the database
  await db.read();

  // Find the index of the ticket to delete
  const idx = db.data.tickets.findIndex(t => t.id === req.params.ticket_id);

  // If not found, return 404
  if (idx === -1) return res.status(404).json({ error: 'Ticket not found' });

  // Store the ticket ID for notification
  const ticketId = db.data.tickets[idx].id;

  // Remove the ticket from the array
  db.data.tickets.splice(idx, 1);

  // Also remove all responses associated with this ticket
  if (db.data.responses) {
    db.data.responses = db.data.responses.filter(r => r.ticket_id !== ticketId);
  }

  // Persist the change to disk
  await db.write();

  // Notify WebSocket clients of the deletion
  notifyTicketUpdate(ticketId, 'deleted');

  // Return 204 No Content
  res.status(204).send();
});

app.post('/api/tickets/:ticket_id/responses', async (req, res) => {

  // Read the latest data from the database
  await db.read();

  // Check if the ticket exists first
  const ticket = db.data.tickets.find(t => t.id === req.params.ticket_id);
  if (!ticket) return res.status(404).json({ error: 'Ticket not found' });

  // Ensure responses array exists
  if (!db.data.responses) db.data.responses = [];

  // Validate required fields
  const { author, message } = req.body;
  if (!author || !message) return res.status(400).json({ error: 'Author and message are required.' });

  // Create the response object
  const response = {
    id: uuidv4(),
    ticket_id: req.params.ticket_id,
    author,
    message,
    created_at: new Date().toISOString()
  };

  // Add the response to the array
  db.data.responses.push(response);

  // Persist the change to disk
  await db.write();

  // Notify WebSocket clients of the new response
  notifyTicketUpdate(req.params.ticket_id, 'response');

  // Return the created response
  res.status(201).json(response);
});

/**
 * @swagger
 * /api/tickets/{ticket_id}/respond:
 *   post:
 *     summary: Add a response to a ticket
 *     parameters:
 *       - in: path
 *         name: ticket_id
 *         schema:
 *           type: string
 *         required: true
 *         description: Ticket ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               author:
 *                 type: string
 *               message:
 *                 type: string
 *     responses:
 *       201:
 *         description: Response added
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 id:
 *                   type: string
 *                 ticket_id:
 *                   type: string
 *                 author:
 *                   type: string
 *                 message:
 *                   type: string
 *                 created_at:
 *                   type: string
 *       404:
 *         description: Ticket not found
 */
app.post('/api/tickets/:ticket_id/respond', async (req, res) => {

  // Read the latest data from the database
  await db.read();

  // Find the ticket to respond to
  const ticket = db.data.tickets.find(t => t.id === req.params.ticket_id);

  // If not found, return 404
  if (!ticket) return res.status(404).json({ error: 'Ticket not found' });

  // Ensure responses array exists
  if (!db.data.responses) db.data.responses = [];

  // Extract author and message from request body
  const { author, message } = req.body;

  // Validate required fields
  if (!author || !message) return res.status(400).json({ error: 'Author and message are required.' });

  // Create the response object
  const response = {
    id: uuidv4(),
    ticket_id: req.params.ticket_id,
    author,
    message,
    created_at: new Date().toISOString()
  };

  // Add the response to the array
  db.data.responses.push(response);

  // Persist the change to disk
  await db.write();

  // Notify WebSocket clients of the new response
  notifyTicketUpdate(ticket.id, 'response');

  // Return the created response
  res.status(201).json(response);
});

/**
 * @swagger
 * /api/tickets/{ticket_id}/status:
 *   post:
 *     summary: Update the status of a ticket
 *     parameters:
 *       - in: path
 *         name: ticket_id
 *         schema:
 *           type: string
 *         required: true
 *         description: Ticket ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               status:
 *                 type: string
 *                 enum: [open, in progress, closed, escalated]
 *     responses:
 *       200:
 *         description: Ticket status updated
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Ticket'
 *       400:
 *         description: Invalid status
 *       404:
 *         description: Ticket not found
 */
app.post('/api/tickets/:ticket_id/status', async (req, res) => {

  // Read the latest data from the database
  await db.read();

  // Find the ticket to update
  const ticket = db.data.tickets.find(t => t.id === req.params.ticket_id);

  // If not found, return 404
  if (!ticket) return res.status(404).json({ error: 'Ticket not found' });

  // Define allowed status values
  const allowedStatuses = ['open', 'in progress', 'closed', 'escalated'];

  // Extract status from request body
  const { status } = req.body;

  // Validate status value
  if (!status || !allowedStatuses.includes(status)) {
    return res.status(400).json({ error: 'Invalid or missing status.' });
  }

  // Update the ticket's status
  ticket.status = status;

  // Persist the change to disk
  await db.write();

  // Notify WebSocket clients of the status update
  notifyTicketUpdate(ticket.id, 'status');

  // Return the updated ticket
  res.json(ticket);
});

// -------------------
// WebSocket Setup
// -------------------

// WebSocket server for real-time ticket update notifications
const wss = new WebSocketServer({ noServer: true });
const clients = new Set();

wss.on('connection', (ws) => {
  // Add the new client to the set
  clients.add(ws);

  // Remove the client when the connection closes
  ws.on('close', () => clients.delete(ws));
});

app.wsServer = wss;

// Upgrade HTTP server to handle WebSocket connections at /ws
const server = app.listen(PORT, () => {
  // Log the server start and documentation URL
  console.log(`Ticketing system API running at http://localhost:${PORT}`);
  console.log(`Swagger docs at http://localhost:${PORT}/api/docs`);
});

server.on('upgrade', (request, socket, head) => {
  // Only handle upgrades for the /ws endpoint
  if (request.url === '/ws') {
    // Upgrade the connection to a WebSocket
    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit('connection', ws, request);
    });
  } else {
    // Destroy the socket for unknown endpoints
    socket.destroy();
  }
});

function notifyTicketUpdate(ticketId, updateType) {
  // Iterate over all connected WebSocket clients
  for (const ws of clients) {
    // Only send if the connection is open
    if (ws.readyState === 1) { // WebSocket.OPEN = 1
      ws.send(JSON.stringify({ ticketId, updateType }));
    }
  }
}

// -------------------
// Static File Serving
// -------------------

// Serve the static index.html at the root
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(express.static(__dirname));

app.get('/', (req, res) => {
  // Serve the main HTML file for the frontend
  res.sendFile(path.join(__dirname, 'index.html'));
});
