from typing import Annotated
from fastapi import FastAPI, Request,Form,WebSocket,UploadFile,File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import hashlib
from datetime import datetime, timedelta
import asyncio
import logging
import colorlog
import json

# Configure colorized logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(levelname)s: %(message)s"))
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI()

templates = Jinja2Templates(directory="./templates")
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
async def login(password: Annotated[str, Form()]):
    # Encrypt the password using a hashing algorithm (e.g., SHA256)
    # encrypted_id = hashlib.sha256(password.encode()).hexdigest()
    # Redirect the user to a page with the encrypted ID
    # return {"item_id": password}
    
    return {"status":1,"redirect": f"/items/{password}"}

@app.get("/item/{item_id}",response_class=HTMLResponse)
async def read_item(item_id,request: Request):
    return templates.TemplateResponse("userPage.html",{"request": request,"item_id": item_id})

@app.get("/js/{file_id}")
async def get_js_file(file_id):
    return FileResponse("./js/{}".format(file_id))

@app.get("/assets/{file_id}")
async def get_assets_file(file_id):
    return FileResponse("./assets/{}".format(file_id))

@app.get("/style/{file_id}")
async def get_assets_file(file_id):
    return FileResponse("./style/{}".format(file_id))

import base64
import io
from PIL import Image
# Dictionary to store websockets
clientWebsockets = {}
# Timeout duration for inactive clients (in seconds)
timeout_duration = 3000

@app.post("/upload-image")
async def upload_image(image:Annotated[str,File()], id:Annotated[str,File()]):
    # # Extract the base64 encoded image data from the data URL
    # image_data = image.split(",")[1]
    # # Decode the base64 image data
    # decoded_image = base64.b64decode(image_data)
    # # Open the image using PIL
    # image = Image.open(io.BytesIO(decoded_image))
    # # Convert the image to JPEG format
    # image = image.convert("RGB")
    # # Save the image to the specified file path
    # image.save("./Test.jpeg", "JPEG")
    
    #Send to other clients and purge dead sockets
    sockets = {}
    try:
        sockets = clientWebsockets[id]
    except:
        return{"message": "This client is not in socketPool"}
    
    current_time = datetime.now()
    delindex =[]

    data = {"image":image,"latex":"Latex here in Future"}
    json_data = json.dumps(data)

    for websocket, last_active_time in sockets.items():
        try:
            await websocket.send_text(json_data)
            sockets[websocket] = current_time
            logger.info("Successfully send")
        except:
            delindex.append(websocket)
            logger.error("A dead socket is found")

    for index in delindex:
        sockets.pop(index)
    return {"message": "Image uploaded and saved successfully.", "id":id}


# Function to purge timeout or closed websockets
async def purge_websockets(clientWebsockets: dict[str, dict]):
    while True:
        clientNum = len(clientWebsockets.items())
        socketNum = 0
        for _,sockets in clientWebsockets.items():
            socketNum += len(sockets.items())
        logger.info("Start purge at {}, {} clients , {} sockets".format(datetime.now(),clientNum,socketNum))
        
        current_time = datetime.now()
        expired_clients = []

        for clientID, sockets in clientWebsockets.items():
            closed_sockets = []
            for websocket, last_active_time in sockets.items():
                if (current_time - last_active_time) > timedelta(seconds=timeout_duration):
                    closed_sockets.append(websocket)

            for websocket in closed_sockets:
                sockets.pop(websocket)

            if not sockets:
                expired_clients.append(clientID)

        for clientID in expired_clients:
            clientWebsockets.pop(clientID)

        
        clientNum = len(clientWebsockets.items())
        socketNum = 0
        for _,sockets in clientWebsockets.items():
            socketNum += len(sockets.items())
        logger.info("End purge at {}, {} clients , {} sockets".format(datetime.now(),clientNum,socketNum))
        
        # Sleep for a certain duration before checking for inactive websockets again
        await asyncio.sleep(timeout_duration)

# WebSocket route
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Receive data from the client
    clientID = await websocket.receive_text()
    logger.info("{} Connected in".format(clientID))
    try:
        socketDict= clientWebsockets[clientID]
    except:
        clientWebsockets[clientID]=dict()
    
    # Update the last active time for the websocket
    clientWebsockets[clientID][websocket] = datetime.now()
    # This will keep websocket alive
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"ping")
        # logger.info(clientWebsockets)
        
# Start the task to check for inactive websockets
asyncio.create_task(purge_websockets(clientWebsockets))