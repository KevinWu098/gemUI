from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import uvicorn
from manager import manager
from fastapi.websockets import WebSocket, WebSocketDisconnect
from selenium_functions import getUrl, navigate, open_browser, scrape, scrapeById, scrapeByXPath
from gemini_functions import extractUI

from starlette.middleware.cors import CORSMiddleware
from typing import Optional
import json
import asyncio


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
            elif (event == "prompt"):
                # scrape the HTML
                html = scrape(browser)
                print("Scraped HTML")
                # TODO: feed image or video feed to gemini
                # give the current URL to Gemini
                url = getUrl(browser)
                print("Got URL: ", url)
                prompt = data["prompt"]
                # give the HTML and the url to gemini
                print("Extracting UI...")
                selector_object = extractUI(prompt, url, html)

                # clean up selector_object, remove the json and backticks
                selector_object = selector_object.replace("`", "").replace("json", "")
                # parse the selector object
                selector_object = json.loads(selector_object)

                # use the selector object to scrape the UI
                elements = []
                if (selector_object["type"] == "xpath"):
                    elements = scrapeByXPath(browser, selector_object["selector"])
                elif (selector_object["type"] == "id"):
                    elements = scrapeById(browser, selector_object["selector"])
                elif (selector_object["type"] == "navigation"):
                    browser = navigate(browser, selector_object["url"])
                else:
                    print(selector_object)
                
                if len(elements):
                    await manager.send_personal_message(
                                                  {
                                                      "event": "action",
                                                      "data": {
                                                          "messageToUser": "Dylan needs to prompt engineer",
                                                          "selectors": selector_object["selector"],
                                                          "html": elements,
                                                      }
                                                  }, websocket)
                elif (selector_object["type"] == "navigation"):
                    await manager.send_personal_message({"event": "thought", "data": {
                        "thought": "I just navigated to " + selector_object["url"]
                    }}, websocket)
                else:
                    await manager.send_personal_message({"event": "thought", "data": {
                        "thought": "I couldn't interact with the browser properly."
                    }}, websocket)
            # elif (event == "navigate"):
            #     url = data["url"]
            #     print("Navigating to: ", url)
            #     browser = navigate(browser, url)
            # elif (event == "scrape"):
            #     print("Scraping...")
            #     html = scrape(browser)
    except WebSocketDisconnect:
        print("Disconnecting...")
        await manager.disconnect(client_id)

if __name__ == "__main__":
    # uvicorn main:app --reload
    # ws://localhost:8000/ws?client_id=123
    uvicorn.run(app, host="0.0.0.0", port=10000)