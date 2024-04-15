from time import sleep
from fastapi import FastAPI
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
from gemini_functions import generate, interpret, navigate_check
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
browser = None


# websocket
@app.websocket("/ws")
# default state of client is none
async def websocket_endpoint(websocket: WebSocket, client_id: Optional[str] = None):
    global active_prompt
    global browser
    if client_id is None:
        client_id = websocket.query_params.get("client_id")

    if client_id is None:
        await websocket.close(code=4001)
        return
    # save this client into server memory
    await manager.connect(websocket, client_id)
    browser = open_browser(browser)
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
                    await navigate_ui(browser, websocket)
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
    nav_check_flag = False
    interpret_flag = False
    generate_flag = False
    max_tries = 3

    while (
        not nav_check_flag or not interpret_flag or not generate_flag and max_tries > 0
    ):
        max_tries -= 1
        try:
            if not nav_check_flag:
                url = getUrl(browser)
                print(f"URL: {url}")
                nav = navigate_check(active_prompt, url)
                print(nav)

                if nav["type"] == "navigate":
                    await manager.send_personal_message(
                        {
                            "event": "thought",
                            "data": {
                                "thought": f"I'm navigating to {nav['url']}",
                            },
                        },
                        websocket,
                    )
                    navigate(browser, nav["url"])
                    print(f"Navigating to {nav['url']}")
                    await asyncio.sleep(1.5)
                nav_check_flag = True

            if not interpret_flag:
                url = getUrl(browser)
                html = scrape(browser)
                take_screenshot(browser)
                img = PIL.Image.open("website.png")

                print("Gemini is interpreting...")
                await manager.send_personal_message(
                    {
                        "event": "thought",
                        "data": {
                            "thought": "I'm interpreting the page...",
                        },
                    },
                    websocket,
                )
                selectors = interpret(active_prompt, url, html, img)
                print(selectors)
                interpret_flag = True

            if not generate_flag:
                print("Gemini is generating...")
                await manager.send_personal_message(
                    {
                        "event": "thought",
                        "data": {
                            "thought": "I'm generating the UI...",
                        },
                    },
                    websocket,
                )
                generated_ui = generate(html, selectors["selectors"], url)
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
                generate_flag = True

        except Exception as e:
            print(e)
            # Optionally, reset specific flags here based on error type or content
            # e.g., if "navigation error" in str(e): nav_check = False
