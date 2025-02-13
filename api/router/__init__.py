"""
Package des routers de l'API Photo Arc
"""

from .router_image import router as image_router
from .router_celery import router as celery_router

__all__ = ['image_router', 'celery_router']
