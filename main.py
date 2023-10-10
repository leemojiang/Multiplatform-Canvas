from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import hashlib
from pydantic import BaseModel


app = FastAPI()
templates = Jinja2Templates(directory="./templates")
class Password(BaseModel):
    password: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
async def login(password: Password):
    # Encrypt the password using a hashing algorithm (e.g., SHA256)
    # encrypted_id = hashlib.sha256(password.encode()).hexdigest()
    # Redirect the user to a page with the encrypted ID
    return {"item_id": password}
    
    return {"redirect": f"/items/{encrypted_id}"}

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}