'''
Fetches an authorization URL from a FastAPI server (backend_server). When a user clicks the authorization link, they are redirected to authenticate themselves. \
Once authenticated, the access token is extracted and used to make an authenticated API call to the FastAPI server to fetch data.
'''
import streamlit as st
import requests

# Function to fetch authorization URL
def fetch_auth_url():
    try:
        response = requests.get("http://localhost:8000/auth_url")
        data = response.json()
        return data["auth_url"]
    except Exception as e:
        st.write(f"Error occurred: {e}")
        return "#"

# Main part of the Streamlit app
def main():
    auth_url = fetch_auth_url()
    st.title("WhoopGPT")
    st.markdown(f"To authorize, [click here]({auth_url})")

    token = st.experimental_get_query_params().get("token", None)
    if token:
        token = token[0]
        st.write(f"Access Token: {token}")  # For debugging

        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(f"http://localhost:8000/some_endpoint?token={token}", headers=headers)
            api_data = response.json()
            st.write(api_data)
        except Exception as e:
            st.write(f"API call failed: {e}")

if __name__ == "__main__":
    main()


