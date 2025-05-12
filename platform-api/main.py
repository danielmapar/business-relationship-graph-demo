from fastapi import FastAPI
from .routes import business, relationship  # Import your router modules

app = FastAPI()

# Include the routers
app.include_router(business.router)
app.include_router(relationship.router)

@app.get("/")
async def read_root():
    return {"Hello": "Intuit"}