from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import business, relationship  # Import your router modules

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the routers
app.include_router(business.router)
app.include_router(relationship.router)

@app.get("/")
async def read_root():
    return {"Hello": "Demo"}