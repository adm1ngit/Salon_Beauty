from fastapi import FastAPI 
from app.api.v1 import auth, client, booking, subscriptions, salon
from app.api.v1 import payments as click
from app.api.v1 import subscriptions
from starlette.middleware.cors import CORSMiddleware
from app.db.init_db import init_db

app = FastAPI(title="Beauty App")
@app.on_event("startup")
def on_startup():
    init_db()
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Routerni ulash
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(client.router, prefix="/api/v1/users", tags=["users"])
app.include_router(salon.router, prefix="/api/v1/salons", tags=["salons"])
app.include_router(booking.router, prefix="/api/v1/bookings", tags=["bookings"])
app.include_router(click.router, prefix="/api/v1/payments", tags=["click"])

app.include_router(subscriptions.router, prefix="/api/v1/subscriptions", tags=["subscriptions"])