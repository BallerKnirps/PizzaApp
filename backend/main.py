from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import asyncio
from uuid import uuid4
import re
import json
import os

img_tag_pattern = re.compile(r'<img[^>]+src="([^"]+)"[^>]*>', re.IGNORECASE)

from getChatId import main as get_messages  # This function fetches messages
from getChatId import get_token

active_clients = []
url_mappings = {}
messages = []
last_update = datetime.now()
token = get_token()



def map_image_urls(messages):
    for message in messages:
        html = message.get("body", {}).get("content", "")
        def replace_img(match):
            real_url = match.group(1)
            if "$value" in real_url:  # only rewrite Graph-hosted image
                uid = str(uuid4())
                url_mappings[uid] = real_url
                return match.group(0).replace(real_url, f"http://localhost:8000/image-proxy/{uid}")
            return match.group(0)

        new_html = img_tag_pattern.sub(replace_img, html)
        message["body"]["content"] = new_html  # overwrite with cleaned html
    return messages


async def send_periodic_updates():
    global messages
    while True:
        new_messages = get_messages() or []
        if not len(messages) or messages[0]["createdDateTime"] != messages[0]["createdDateTime"]:
            messages = map_image_urls(new_messages)
            for client in active_clients.copy():
                try:
                    await client.send_json(messages)
                except Exception as e:
                    print(f"Error sending periodic update: {e}")
                    active_clients.remove(client)
        await asyncio.sleep(60)


def create_files():
    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")
    if not os.path.exists("driverhistory.json"):
        with open("driverhistory.json", "w") as file:
            json.dump([], file)  # Create an empty list
    if not os.path.exists("messages.json"):
        with open("messages.json", "w") as file:
            json.dump([], file)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global messages # initial preload
    background_task = asyncio.create_task(send_periodic_updates())
    create_files()
    yield
    background_task.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws/teams")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_clients.append(websocket)

    # Immediately send the latest messages on connect
    try:
        await websocket.send_json(messages)
        while True:
            await websocket.receive_text()  # keep alive
    except Exception as e:
        print(f"Client disconnected or error: {e}")
    finally:
        if websocket in active_clients:
            active_clients.remove(websocket)


@app.get("/image-proxy/{id}")
async def image_proxy(id: str):
    print("image proxy called")

    url = url_mappings.get(id)
    if not url:
        raise HTTPException(status_code=400, detail="Invalid or missing image mapping")

    global token
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            })
        except httpx.RequestError:
            token = get_token()
            resp = await client.get(url, headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            })
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail="Image fetch failed")
        return StreamingResponse(resp.aiter_bytes(), media_type=resp.headers.get("Content-Type", "image/png"))



@app.get("/driver-history")
async def driver_history(request: Request):
    try:
        with open("driverhistory.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


@app.post("/driver-history")
async def update_driver_history(request: Request):
    data = await request.json()
    with open("driverhistory.json", "r+") as file:
        try:
            stored = json.load(file)
        except json.JSONDecodeError:
            stored = []
        stored.append(data["driver"])
        file.seek(0)
        json.dump(stored, file, indent=4)


    # write messages to messages.json
    with open("messages.json", "r+") as file:
        stored = json.load(file)
        stored.extend(messages)
        file.seek(0)
        json.dump(stored, file, indent=4)


    return {"status": "success"}


@app.get("/pdf-names")
async def get_pdf_names():
    return [pdf for pdf in  os.listdir("pdfs")]


@app.get("/pdf/{file_name}")
async def get_pdf(file_name: str):
    try:
        file = open(f"pdfs/{file_name}", "rb")  # Do NOT use 'with' here!
        headers = {"Content-Disposition": f'inline; filename="{file_name}"'}
        return StreamingResponse(file, media_type="application/pdf", headers=headers)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/messages")
async def history_messages(request: Request):
    try:
        with open("messages.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Only for manual running
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
