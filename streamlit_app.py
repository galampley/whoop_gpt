'''
Fetches an authorization URL from a FastAPI server (auth_server). When a user clicks the authorization link, they are redirected to authenticate themselves. \
Once authenticated, the access token is extracted and used to make an authenticated API call to the FastAPI server to fetch data.
'''
import streamlit as st
import requests

# Function to fetch authorization URL
def fetch_auth_url():
    try:
        # response = requests.get("http://localhost:8000/auth_url")
        response = requests.get("https://whoop-gpt-45ade1b84fc3.herokuapp.com/")
        data = response.json()
        return data["auth_url"]
    except Exception as e:
        st.write(f"Error occurred: {e}")
        return "#"

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Main part of the Streamlit app
def main():
    st.image("Logo/Wordmark/WHOOP Logo Black@3x.png", caption=None, use_column_width=True)
    st.write("")

    auth_url = fetch_auth_url()
    st.title("WhoopGPT")
    st.markdown(f"To authorize, [click here]({auth_url})")
    st.markdown("**Note:** Authorization only lasts for 60 minutes. After 60 minutes, reauthorize with 'click here'")  # This line informs the user about the time limit

    token = st.experimental_get_query_params().get("token", None)
    
    if token:
        token = token[0]
        # st.write(f"Access Token: {token}")  # For debugging

        # New feature: Query through OpenAI
        user_input = st.text_area("Enter your query:")

        if st.button("Submit"):
            # Fetch the bot's response
            # response = requests.post("http://localhost:8001/query", json={"query": user_input, "token": token})
            response = requests.post("https://whoop-gpt-45ade1b84fc3.herokuapp.com/", json={"query": user_input, "token": token})
            bot_reply = response.json().get("response", "Could not fetch response")

            # Update conversation history in session state
            st.session_state.conversation_history.append({"user": user_input, "bot": bot_reply})

            # Display the bot's reply
            st.write(f"Answer: {bot_reply}")

        # Show conversation history
        st.subheader("Conversation History")
        for conversation in reversed(st.session_state.conversation_history):
            st.markdown(f"**You:**\n{conversation['user']}\n\n**Bot:**\n{conversation['bot']}")

        # Button to clear conversation history
        if st.button("Clear Conversation History"):
            st.session_state.conversation_history = []
            st.write("Conversation history has been cleared.")

if __name__ == "__main__":
    main()

