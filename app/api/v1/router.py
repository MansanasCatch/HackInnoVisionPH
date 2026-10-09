"""Aggregates every v1 endpoint router."""

from fastapi import APIRouter

from app.api.v1.endpoints import ai, device, health, learning_resources, onboarding, study_sessions

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(onboarding.router)
api_router.include_router(device.router)
api_router.include_router(ai.router)
api_router.include_router(learning_resources.router)
api_router.include_router(study_sessions.router)
