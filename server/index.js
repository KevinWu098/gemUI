import { WebSocketServer } from "ws";
import dotenv from "dotenv";
import { openBrowser } from "./puppeteer.js";

dotenv.config();

const wss = new WebSocketServer({ port: 8080 });
// connect using ws://localhost:8080

let browser = null;

wss.on("connection", function connection(ws) {
  ws.on("error", console.error);

  ws.on("message", function message(data) {
    // parse as JSON
    const dataJSON = JSON.parse(data);
    const event = dataJSON.event;
    if (event) {
      // handle event
      console.log("Received event:", event);
      if (event === "start") {
        console.log("starting puppeteer");
        // start the puppeteer browser
        (async () => {
          await openBrowser(browser);
        })();
      }
    }
  });

  ws.send("something");
});
