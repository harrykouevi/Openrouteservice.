from fastapi import FastAPI
from app.api.v1.routes import router as v1_router
from app.api.routes import router as v2_router
from fastapi.middleware.cors import CORSMiddleware
from app.api.middleware import BearerTokenMiddleware


app = FastAPI(title="FastAPI Project with ORS")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=[""],
    allow_headers=["*"],
)

# Ajout de ton middleware personnalisé
# Activation du middleware uniquement sur certaines routes
app.add_middleware(BearerTokenMiddleware, protected_paths=[
   
    ])
 # "/api/v1/issues-in-zone"
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router)




