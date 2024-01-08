from fastapi import FastAPI
from fast_auth import auth_router
from query import query_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:8501"],  # Update this to the domain where your Streamlit app will run
    allow_origins=["https://whoopgpt-5srrxenqyvgshz5ccbqhda.streamlit.app"],  # Update this to the domain where your Streamlit app will run
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(query_router)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}

