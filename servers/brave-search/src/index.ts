import { mcpServer } from "./mcp-server.js";
import { serveSse } from "./sse-server.js";

serveSse(mcpServer);
