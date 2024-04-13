import { WebSocketServer } from "ws";
import dotenv from "dotenv";

dotenv.config();

const wss = new WebSocketServer({ port: 8080 });
// connect using ws://localhost:8080

wss.on("connection", function connection(ws) {
  ws.on("error", console.error);

  ws.on("message", function message(data) {
    console.log("received: %s", data);
  });

  ws.send("something");
});
