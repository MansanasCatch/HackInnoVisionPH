"""Aggregates every v1 endpoint router."""

from fastapi import APIRouter

from app.api.v1.endpoints import device, health, onboarding

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(onboarding.router)
api_router.include_router(device.router)
