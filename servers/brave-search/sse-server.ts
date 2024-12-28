import express from "express";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { IncomingMessage, ServerResponse } from "http";
import { type Server } from "@modelcontextprotocol/sdk/server/index.js";

export function makeSseServer(mcpServer: Server) {
  const activeTransports = new Map<string, SSEServerTransport>();

  const app = express();

  // Middleware to parse JSON bodies
  app.use(express.json());

  // Health check endpoint
  app.get("/health", (req: express.Request, res: express.Response) => {
    res.json({ status: "ok" });
  });

  // SSE endpoint
  app.get("/sse", (req: express.Request, res: express.Response) => {
    // Set headers for SSE
    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    // Enable CORS if needed
    res.setHeader("Access-Control-Allow-Origin", "*");

    // Create transport and connect server
    const transport = new SSEServerTransport("messages", res);
    console.log(transport.sessionId);

    // Store the transport with its session ID
    const sessionId = transport.sessionId;
    activeTransports.set(sessionId, transport);

    mcpServer.connect(transport);

    // Handle client disconnect
    req.on("close", () => {
      activeTransports.delete(sessionId);
      transport.close();
    });
  });
  // Add the POST message handler
  app.post("/messages", async (req: express.Request, res: express.Response) => {
    const sessionId = req.query.sessionId as string;

    if (!sessionId) {
      res.status(400).json({ error: "Missing sessionId parameter" });
      return;
    }

    const transport = activeTransports.get(sessionId);

    if (!transport) {
      res.status(404).json({ error: "Session not found" });
      return;
    }

    try {
      console.log("Handling POST message for session ID:", sessionId);
      console.log(req.body);

      await transport.handlePostMessage(req as IncomingMessage, res, req.body);
      console.log("Handling POST message for session ID:", sessionId);
    } catch (error) {
      console.error("Error handling POST message:", error);
      res.status(500).json({ error: "Failed to handle message" });
    }
  });

  // CORS support for the POST endpoint
  app.options("/messages", (req: express.Request, res: express.Response) => {
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");
    res.setHeader("Access-Control-Max-Age", "86400"); // 24 hours
    res.status(204).end();
  });

  // Error handling middleware
  app.use(
    (
      err: Error,
      req: express.Request,
      res: express.Response,
      next: express.NextFunction
    ) => {
      console.error(err.stack);
      res.status(500).json({ error: "Something broke!" });
    }
  );
  return app;
}

export function serveSse(mcpServer: Server) {
  const port = process.env.PORT || 3000;

  // Start the server
  const app = makeSseServer(mcpServer);
  app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
  });
}
