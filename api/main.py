from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from api.startup import startup_event
from pathlib import Path
import os

from api.routes import auth_routes, draw_routes, admin_routes, payment_routes, password_routes, verification_routes, notification_routes

# For Vercel serverless function
app = FastAPI(title="Win Prize Lucky Draw API") 

app.add_event_handler("startup", startup_event)
BASE_DIR = Path(__file__).parent.parent.absolute()
 
DATA_DIR = Path("/tmp/data") if os.getenv("VERCEL") else BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)
 
if os.getenv("VERCEL"):
    import shutil
    source_data = BASE_DIR / "data"

    if source_data.exists():
        for file in source_data.glob("*.json"):
            target = DATA_DIR / file.name
            if not target.exists():
                shutil.copy2(file, target)
 
os.environ["DATA_DIR"] = str(DATA_DIR)
 
# Fix static files mounting for Vercel
static_dir = BASE_DIR / "static"
if static_dir.exists():
    # In Vercel, the static files are served from the root /static path
    app.mount("/static", StaticFiles(directory=str(static_dir), html=True), name="static")
    print(f"Static directory mounted: {static_dir}")
else:
    print(f"Static directory not found: {static_dir}")

templates_dir = BASE_DIR / "templates"
if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))
    print(f"Templates directory found: {templates_dir}")
else:
    print(f"Templates directory not found: {templates_dir}")
    templates = None

app.include_router(auth_routes.router)
app.include_router(draw_routes.router)
app.include_router(admin_routes.router)
app.include_router(payment_routes.router)
app.include_router(password_routes.router)
app.include_router(verification_routes.router) 
app.include_router(notification_routes.router)    


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    return HTMLResponse(content="<h1>Templates not found</h1>")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if templates:
        return templates.TemplateResponse("login.html", {"request": request})
    return HTMLResponse(content="<h1>Login page not found</h1>")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    if templates:
        return templates.TemplateResponse("register.html", {"request": request})
    return HTMLResponse(content="<h1>Register page not found</h1>")

@app.get("/verify", response_class=HTMLResponse)
async def verify_page(request: Request):
    return templates.TemplateResponse("verify.html", {"request": request})

@app.get("/confirm", response_class=HTMLResponse)
async def confirm_page(request: Request):
    if templates:
        return templates.TemplateResponse("confirm.html", {"request": request})
    return HTMLResponse(content="<h1>Confirm page not found</h1>")

@app.get("/payment-status", response_class=HTMLResponse)
async def payment_status_page(request: Request):
    if templates:
        return templates.TemplateResponse("payment-status.html", {"request": request})
    return HTMLResponse(content="<h1>Payment status page not found</h1>")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    if templates:
        return templates.TemplateResponse("admin.html", {"request": request})
    return HTMLResponse(content="<h1>Admin page not found</h1>")

@app.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request):
    if templates:
        return templates.TemplateResponse("notifications.html", {"request": request})
    return HTMLResponse(content="<h1>Notifications page not found</h1>")

@app.get("/winner", response_class=HTMLResponse)
async def winners_page(request: Request):
    if templates:
        return templates.TemplateResponse("winner.html", {"request": request})
    return HTMLResponse(content="<h1>Winner page not found</h1>")

# Health check endpoint for Vercel
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "static_dir_exists": static_dir.exists() if static_dir else False, 
        "templates_dir_exists": templates_dir.exists() if templates_dir else False
    }
 
# This is for Vercel serverless
@app.get("/api")
async def root():
    return {"message": "Win Prize API"}
