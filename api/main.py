from fastapi import FastAPI
from config.logging_config import configure_logging
from router import router_celery, router_image

# Configuration du logging
logger = configure_logging()

app = FastAPI(title="Photo Arc API")

# Enregistrement des routers
app.include_router(router_celery.router)
app.include_router(router_image.router)

@app.get("/")
async def root():
    logger.info("Requête reçue sur la route racine")
    return {"message": "Bienvenue sur l'API Photo Arc"}