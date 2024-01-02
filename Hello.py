import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import urllib.parse
   

# Replace these with your client details
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_uri = st.secrets["redirect_url"]  # This must match the redirect URI in your OAuth provider settings
# redirect_url= "https://orange-happiness-v5vqwj5qp7q2p996-8501.app.github.dev/"
scope='email profile'
authorization_endpoint = 'https://accounts.google.com/o/oauth2/auth'
token_endpoint = 'https://oauth2.googleapis.com/token'
userinfo_endpoint = 'https://www.googleapis.com/oauth2/v1/userinfo'
st.sidebar.markdown(f"Secrets:\n {st.secrets}")
st.sidebar.markdown(f"State:\n {st.session_state}")
st.sidebar.markdown(f"Params:\n {st.experimental_get_query_params()}")

import requests

def exchange_code_for_token(code):
    token_url = 'https://oauth2.googleapis.com/token'
    # Prepare the data for the token request
    data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    # Make a POST request to the token endpoint
    response = requests.post(token_url, data=data)
    response_data = response.json()
    # Handle possible errors
    if response.status_code != 200:
        raise Exception("Failed to retrieve token: " + response_data.get('error_description', ''))
    return response_data['access_token']

def get_user_info(access_token):
    user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(user_info_url, headers=headers)
    user_info = response.json()
    # Handle possible errors
    if response.status_code != 200:
        raise Exception("Failed to retrieve user info: " + user_info.get('error_description', ''))
    return user_info

def nav_to(url):
    nav_script = """
        <meta http-equiv="refresh" content="0; url='%s'">
    """ % (url)
    st.write(nav_script, unsafe_allow_html=True)

def main():
    st.title('OAuth with Streamlit')

    # Initialize the session
    session = OAuth2Session(client_id, client_secret, scope=scope, redirect_uri=redirect_uri)

    # Check if the user is logged in
    if 'user_info' in st.session_state:
        user_info = st.session_state['user_info']
        st.write(f"1. Welcome {user_info['name']}!")
        # Do the main thing here
    elif 'scope' in st.experimental_get_query_params():
        # Exchange the code for a token
        token = exchange_code_for_token(st.experimental_get_query_params()['code'])
        user_info = get_user_info(token)
        st.session_state['token'] = token
        st.session_state['user_info'] = user_info
        st.session_state['states_seen'] = "Passed 2"
        st.write("2. Welcome, ", user_info['name'])
        st.experimental_rerun()
    else:
        # Generate the authorization URL and state, save the state
        uri, state = session.create_authorization_url(authorization_endpoint)
        st.session_state['state'] = state

        # Display the login link
        st.markdown(f'[Login with Google]({uri})')

        # Handle the callback from the OAuth provider
        params = st.experimental_get_query_params()
        if 'code' in params and params.get('state') == st.session_state.get('state'):
            # Exchange the code for a token
            token = session.fetch_token(token_endpoint, authorization_response=st.experimental_get_url())
            st.session_state['token'] = token
            st.experimental_rerun()

if __name__ == '__main__':
    main()




