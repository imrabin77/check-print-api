from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import engine, Base
from app.core.security import hash_password
from app.api import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default users
    from sqlalchemy import select
    from app.core.database import async_session_factory
    from app.models.user import User

    async with async_session_factory() as session:
        result = await session.execute(select(User).where(User.email == "admin@checkprint.local"))
        if not result.scalar_one_or_none():
            for email, pwd, name, role in [
                ("admin@checkprint.local", "admin123", "System Admin", "ADMIN"),
                ("clerk@checkprint.local", "clerk123", "Default Clerk", "CLERK"),
                ("viewer@checkprint.local", "viewer123", "Default Viewer", "VIEWER"),
            ]:
                session.add(User(
                    email=email, hashed_password=hash_password(pwd),
                    full_name=name, role=role,
                    is_active=True,
                ))
            await session.commit()

    yield


app = FastAPI(title="Check Print API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
