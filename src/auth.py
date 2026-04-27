import streamlit as st
from firebase_admin import firestore
from firebase_admin import auth
import json
import requests
from firebase_init import init_firebase

init_firebase()

def app():
    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown("# Welcome to :violet[MedCliniQ]")
        st.markdown("##### Your AI Medical Assistant")
        st.divider()

        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "username" not in st.session_state:
            st.session_state.username = ""
        if "useremail" not in st.session_state:
            st.session_state.useremail = ""
        if "signedout" not in st.session_state:
            st.session_state["signedout"] = False
        if "signout" not in st.session_state:
            st.session_state["signout"] = False
        if "auth_mode" not in st.session_state:
            st.session_state["auth_mode"] = "Login"
        if "show_reset" not in st.session_state:
            st.session_state["show_reset"] = False

        def sign_up_with_email_and_password(email, password, username=None, return_secure_token=True):
            try:
                rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
                payload = {
                    "email": email,
                    "password": password,
                    "returnSecureToken": return_secure_token,
                }
                if username:
                    payload["displayName"] = username
                r = requests.post(
                    rest_api_url,
                    params={"key": "REMOVED"},
                    json=payload,
                )
                data = r.json()
                if r.status_code == 200:
                    return data.get("email")
                else:
                    st.error(data.get("error", {}).get("message", "Signup failed"))
                    return None
            except Exception as e:
                st.error(f"Signup failed: {e}")
                return None

        def sign_in_with_email_and_password(email=None, password=None, return_secure_token=True):
            rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
            try:
                payload = {"returnSecureToken": return_secure_token}
                if email:
                    payload["email"] = email
                if password:
                    payload["password"] = password
                payload = json.dumps(payload)
                r = requests.post(
                    rest_api_url,
                    params={"key": "REMOVED"},
                    data=payload,
                )
                data = r.json()
                if "error" in data:
                    return None
                return {
                    "email": data["email"],
                    "username": data.get("displayName"),
                    "user_id": data.get("localId"),
                }
            except Exception as e:
                st.warning(f"Signin failed: {e}")

        def reset_password(email):
            try:
                rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
                payload = json.dumps({"email": email, "requestType": "PASSWORD_RESET"})
                r = requests.post(
                    rest_api_url,
                    params={"key": "REMOVED"},
                    data=payload,
                )
                if r.status_code == 200:
                    return True, "Reset email sent"
                else:
                    return False, r.json().get("error", {}).get("message")
            except Exception as e:
                return False, str(e)

        if not st.session_state["signedout"]:
            # Mode toggle buttons
            col_login, col_signup = st.columns(2)
            with col_login:
                if st.button(
                    "Login",
                    use_container_width=True,
                    type="primary" if st.session_state["auth_mode"] == "Login" else "secondary",
                ):
                    st.session_state["auth_mode"] = "Login"
                    st.session_state["show_reset"] = False
                    st.rerun()
            with col_signup:
                if st.button(
                    "Sign Up",
                    use_container_width=True,
                    type="primary" if st.session_state["auth_mode"] == "Sign up" else "secondary",
                ):
                    st.session_state["auth_mode"] = "Sign up"
                    st.session_state["show_reset"] = False
                    st.rerun()

            st.write("")

            # Login form
            if st.session_state["auth_mode"] == "Login":
                with st.form("login_form"):
                    email = st.text_input("Email Address")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

                if submitted:
                    userinfo = sign_in_with_email_and_password(email, password)
                    if userinfo:
                        st.session_state.username = userinfo["username"]
                        st.session_state.useremail = userinfo["email"]
                        st.session_state.user_id = userinfo["user_id"]
                        st.session_state.email_input = email
                        st.session_state.password_input = password
                        st.session_state.authenticated = True
                        st.session_state.signedout = True
                        st.session_state.signout = True
                        st.rerun()
                    else:
                        st.error("Login failed. Please check your email and password.")

                # Forgot password toggle
                if st.button("Forgot password?", use_container_width=False):
                    st.session_state["show_reset"] = not st.session_state["show_reset"]

                if st.session_state["show_reset"]:
                    st.divider()
                    with st.form("reset_form"):
                        reset_email = st.text_input("Enter your email address")
                        reset_submitted = st.form_submit_button("Send Reset Link", use_container_width=True)
                    if reset_submitted:
                        success, message = reset_password(reset_email)
                        if success:
                            st.success("Password reset email sent successfully.")
                        else:
                            st.warning(f"Password reset failed: {message}")

            # Sign up form
            else:
                with st.form("signup_form"):
                    username = st.text_input("Username")
                    email = st.text_input("Email Address")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                if submitted:
                    user = sign_up_with_email_and_password(email=email, password=password, username=username)
                    if user:
                        st.success("Account created successfully!")
                        st.info("Please switch to Login to continue.")
                        st.balloons()
                    else:
                        st.warning("Account was not created.")
