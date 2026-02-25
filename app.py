import os
import shutil
import uvicorn
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

# Basic Setup
load_dotenv()
app = FastAPI()

# Session Security
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SESSION_SECRET", "exam_mind_ultra_pro_2026")
)

# Folder Safety Checks
for folder in ["static", "templates", "uploads", "vectorstore"]:
    os.makedirs(folder, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Import internal modules
from auth import init_oauth
from analytics import get_top_topics
oauth = init_oauth()

# ==========================
# ROUTES
# ==========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    if user:
        return RedirectResponse("/dashboard")
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    return await oauth.google.authorize_redirect(request, request.url_for("auth"))

@app.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get("userinfo")
    if user:
        request.session["user"] = dict(user)
    return RedirectResponse("/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/")
    
    # Session se result uthao aur turant clear kar do taaki refresh pe gayab ho jaye
    result = request.session.pop("last_result", None)
    question = request.session.pop("last_question", None)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "name": user.get("name"), 
        "picture": user.get("picture"), 
        "top_topics": get_top_topics(),
        "result": result,
        "question": question
    })

@app.post("/ask")
async def ask(request: Request, query: str = Form(...)):
    from rag import ask_question 
    
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/")
    
    response = ask_question(query)
    
    # Result ko session mein temporarily save karo
    request.session["last_result"] = response["answer"]
    request.session["last_question"] = query
    
    # Answer dikhane ke liye dashboard par bhej do (Redirect)
    return RedirectResponse("/dashboard", status_code=303)

@app.post("/upload")
async def upload_pdf(request: Request, pdf_file: UploadFile = File(...)):
    from ingest import process_file
    
    if not request.session.get("user"):
        return RedirectResponse("/")
    
    file_path = os.path.join("uploads", pdf_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(pdf_file.file, buffer)
    
    process_file(file_path, pdf_file.filename.replace(".pdf", ""))
    return RedirectResponse("/dashboard?msg=UploadSuccess")

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)