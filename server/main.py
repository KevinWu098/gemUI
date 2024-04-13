from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import uvicorn
from manager import manager
from fastapi.websockets import WebSocket, WebSocketDisconnect
from selenium_functions import navigate, open_browser, scrape

from starlette.middleware.cors import CORSMiddleware
from typing import Optional

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3000/*",
    # "http://localhost",
    # "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}

# websocket
@app.websocket("/ws")
# default state of client is none
async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = None):
    if client_id is None:
        client_id = websocket.query_params.get("client_id")

    if client_id is None:
        await websocket.close(code=4001)
        return
    # save this client into server memory
    await manager.connect(websocket, client_id)      
    browser = None
    try:
        while True:
            data = await websocket.receive_json()
            event = data["event"]
            print(event)
            if (event == "start"):
                browser = open_browser(browser)
            elif (event == "navigate"):
                url = data["url"]
                print("Navigating to: ", url)
                browser = navigate(browser, url)
            elif (event == "scrape"):
                print("Scraping...")
                html = scrape(browser)
    except WebSocketDisconnect:
        print("Disconnecting...")
        await manager.disconnect(client_id)

if __name__ == "__main__":
    # uvicorn main:app --reload
    # ws://localhost:8000/ws?client_id=123
    uvicorn.run(app, host="0.0.0.0", port=10000)