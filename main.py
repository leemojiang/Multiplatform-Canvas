from typing import Annotated
from fastapi import FastAPI, Request,Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import hashlib
from pydantic import BaseModel


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

@app.get("/item/{item_id}")
async def read_item(item_id):
    return templates.TemplateResponse("page.html", {"request": request})