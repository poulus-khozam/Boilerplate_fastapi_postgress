# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, totp
from database import Base, engine

# This will create the tables in the database if they don't exist
# You might want to manage this with Alembic in a production environment
Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:5173",  # The origin of your Vue.js front-end
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods: GET, POST, etc.
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth.router, tags=["Authentication"])
app.include_router(totp.router, tags=["TOTP"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the NPC Users API"}
