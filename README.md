# Whoop_GPT

## Introduction
This project aims to query data from Whoop fitness bands and provide insights and answers based on the user's data. The application is built using FastAPI for backend services and Streamlit for the frontend.

## Features
- OAuth 2.0 Authentication with Whoop API
- Data retrieval and analysis
- User-friendly Streamlit interface
- Heroku-ready for easy deployment

## Project Structure
```
.
├── auth_server.py         # Handles OAuth 2.0 authentication
├── query_server.py        # Responsible for data queries and retrieval
├── streamlit_app.py       # Streamlit application
├── main.py                # Main FastAPI application
├── wrapped_auth.py        # Wrapper for OAuth functions
├── requirements.txt       # Project dependencies
└── Procfile               # Heroku deployment configuration
```

## Installation
1. Clone the repository
2. Install the dependencies
    ```
    pip install -r requirements.txt
    ```

## Usage
### Local Development
1. Run the FastAPI application
    ```
    uvicorn main:main_app --reload
    ```
2. Run the Streamlit application
    ```
    streamlit run streamlit_app.py
    ```
### Deployment
Follow the instructions in the `Procfile` for Heroku deployment.

## Contributing
Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.