from fastapi import FastAPI
from fastapi.routing import APIRouter
from auth_server import app as auth_app  # Assuming your FastAPI app in auth_server.py is named 'app'
from query_server import app as query_app  # Assuming your FastAPI app in query_server.py is named 'app'

main_app = FastAPI()

# Mounting the auth_server and query_server applications
main_app.mount("/auth", auth_app)
main_app.mount("/query", query_app)

# You can also add more routes specifically for main_app if needed
router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "This is the main app."}

main_app.include_router(router)
