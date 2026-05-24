from fastapi import APIRouter
from app.api.v1 import auth, projects, instagram, admin, nilagravity

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(instagram.router, prefix="/instagram", tags=["instagram"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(nilagravity.router, prefix="/nilagravity", tags=["nilagravity"])
