import os
from pathlib import Path
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.services.db import init_db
from backend.routes.products import router as products_router
from backend.routes.chat import router as chat_router
from backend.routes.auth import router as auth_router
from backend.routes.admin import router as admin_router
from backend.routes.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and seed initial demo data
    init_db()
    yield


app = FastAPI(
    title="Queen Sheba API",
    description="Intentionally vulnerable AI e-commerce demonstration backend with authentication and admin panel.",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(products_router)
app.include_router(chat_router)

# Mount frontend directory for seamless serving
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    if (frontend_dir / "css").exists():
        app.mount("/css", StaticFiles(directory=frontend_dir / "css"), name="css")
    if (frontend_dir / "js").exists():
        app.mount("/js", StaticFiles(directory=frontend_dir / "js"), name="js")
    if (frontend_dir / "images").exists():
        app.mount("/images", StaticFiles(directory=frontend_dir / "images"), name="images")

    @app.get("/")
    async def serve_index():
        return FileResponse(frontend_dir / "index.html")

    @app.get("/login")
    @app.get("/signin")
    async def serve_login():
        login_file = frontend_dir / "login.html"
        if login_file.exists():
            return FileResponse(login_file)
        return FileResponse(frontend_dir / "index.html")

    @app.get("/signup")
    async def serve_signup():
        signup_file = frontend_dir / "signup.html"
        if signup_file.exists():
            return FileResponse(signup_file)
        return FileResponse(frontend_dir / "index.html")

    @app.get("/admin")
    async def serve_admin():
        admin_file = frontend_dir / "admin.html"
        if admin_file.exists():
            return FileResponse(admin_file)
        return FileResponse(frontend_dir / "index.html")

    @app.get("/account")
    async def serve_account():
        account_file = frontend_dir / "account.html"
        if account_file.exists():
            return FileResponse(account_file)
        return FileResponse(frontend_dir / "index.html")

    @app.get("/products")
    async def serve_products():
        prod_file = frontend_dir / "products.html"
        if prod_file.exists():
            return FileResponse(prod_file)
        return FileResponse(frontend_dir / "index.html")

    @app.get("/assistant")
    async def serve_assistant():
        asst_file = frontend_dir / "assistant.html"
        if asst_file.exists():
            return FileResponse(asst_file)
        return FileResponse(frontend_dir / "index.html")

    @app.get("/about")
    async def serve_about():
        about_file = frontend_dir / "about.html"
        if about_file.exists():
            return FileResponse(about_file)
        return FileResponse(frontend_dir / "index.html")


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "Queen Sheba Backend",
        "environment": "INTENTIONALLY VULNERABLE AI DEMO",
        "prompt_firewall": "OFF"
    }
