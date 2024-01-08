from fastapi import FastAPI
from auth_server import auth_router
from query_server import query_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(query_router)
