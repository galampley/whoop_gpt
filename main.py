from fastapi import FastAPI
from fast_auth import auth_router
from query import query_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(query_router)
