from time import sleep
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import uvicorn
from manager import manager
from fastapi.websockets import WebSocket, WebSocketDisconnect
from selenium_functions import (
    click,
    getUrl,
    navigate,
    open_browser,
    scrape,
    scrapeById,
    scrapeByXPath,
    selenium_type,
    take_screenshot,
)
from gemini_functions import generate, interpret
import PIL.Image

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


active_prompt = ""


# websocket
@app.websocket("/ws")
# default state of client is none
async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = None):
    global active_prompt
    if client_id is None:
        client_id = websocket.query_params.get("client_id")

    if client_id is None:
        await websocket.close(code=4001)
        return
    # save this client into server memory
    await manager.connect(websocket, client_id)
    browser = open_browser()
    try:
        while True:
            data = await websocket.receive_json()
            event = data["event"]
            print(event)
            if event == "start":
                browser = open_browser(browser)
            elif event == "prompt":
                active_prompt = data["prompt"]
                await navigate_ui(browser, websocket)

            elif event == "userAction":
                selector = data["id"]  # will be used to query
                element = data["element"]  # the type of input/action
                if "value" in data:
                    value = data["value"]
                else:
                    value = None

                if element == "button":
                    click(browser, selector)
                    sleep(1.5)
                    await navigate_ui(browser, data, websocket)
                elif element == "input":
                    selenium_type(browser, selector, value)
                else:
                    print("Unknown element type")
                # done processing action on remote browser

                await manager.send_personal_message({"event": "done"}, websocket)
            elif event == "debug":
                elements = scrapeByXPath(browser, [data["xpath"]])
                print(elements)
    except WebSocketDisconnect:
        print("Disconnecting...")
        await manager.disconnect(client_id)


if __name__ == "__main__":
    # uvicorn main:app --reload
    # ws://localhost:8000/ws?client_id=123
    uvicorn.run(app, host="0.0.0.0", port=10000)


async def navigate_ui(browser, websocket):
    try:
        global active_prompt
        # scrape the HTML
        html = scrape(browser)
        print("Scraped HTML")
        take_screenshot(browser)
        img = PIL.Image.open("website.png")
        # give the current URL to Gemini
        url = getUrl(browser)
        print("Got URL: ", url)

        # give the HTML and the url to gemini
        print("Gemini is interpreting...")
        selectors = interpret(active_prompt, url, html, img)

        print("Gemini is generating...")
        generated_ui = generate(html, selectors, url)
        print("Gemini is done...")

        await manager.send_personal_message(
            {
                "event": "ui",
                "data": {
                    "html": generated_ui,
                },
            },
            websocket,
        )
    except Exception as e:
        print(e)
