import express from "express";
import dotenv from "dotenv";
import cors from "cors";
import http from "http";
import { Server } from "socket.io";

// load up dotenv stuff
dotenv.config();

const app = express();
const port = 5000;

// create the socket server
const server = http.createServer(app);
const io = new Server(server);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(
  cors({
    origin: "*",
  })
);

app.get("/", (req, res) => {
  res.send("Hello World!");
});

io.on("connection", (socket) => {
  console.log(`a user connected with id ${socket.id}`);
});

app.listen(port, () => {
  console.log(`Example app listening on http://localhost:${port}`);
});
