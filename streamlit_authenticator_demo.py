import yaml
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import RegisterError, LoginError

# Load the config file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

st.image('logo.png')

# Create the authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Function to display the login page
def login_page():
    # Create a login widget
    try:
        authenticator.login()
    except LoginError as e:
        st.error(e)

    if st.session_state.get("authentication_status"):
        home_page()  # Redirect to home page if logged in
    elif st.session_state.get("authentication_status") is False:
        st.error('Username/password is incorrect')
    elif st.session_state.get("authentication_status") is None:
        st.warning('Please enter your username and password')

    # Create new account button only if not logged in
    if not st.session_state.get("authentication_status"):
        if st.button("Create new account"):
            registration_page()

# Function to display the registration page
def registration_page():
    st.subheader("Register a New User")
    try:
        (email_of_registered_user,
         username_of_registered_user,
         name_of_registered_user) = authenticator.register_user(pre_authorization=False)
        if email_of_registered_user:
            st.success('User registered successfully! You can now log in.')
            st.button("Back to Login", on_click=login_page)  # Button to go back to login
    except RegisterError as e:
        st.error(e)

# Function to display the home page
def home_page():
    st.success(f'Welcome *{st.session_state["name"]}*')
    st.title('Home Page')

    # Logout button
    if st.button("Log Out"):
        authenticator.logout()
        st.experimental_rerun()  # Refresh the page after logging out

# Render the login page initially
login_page()
