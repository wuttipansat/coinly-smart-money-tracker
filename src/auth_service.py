import streamlit as st

from src.supabase_client import create_supabase_client, get_supabase


def init_auth_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "user" not in st.session_state:
        st.session_state.user = None

    if "supabase" not in st.session_state:
        st.session_state.supabase = create_supabase_client()


def save_auth_session(response, supabase_client):
    st.session_state.supabase = supabase_client
    st.session_state.authenticated = True

    st.session_state.user = {
        "id": response.user.id,
        "email": response.user.email,
    }


def register_user(email: str, password: str):
    email = email.lower().strip()

    if not email or not password:
        return False, "Please enter email and password."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    supabase = create_supabase_client()

    response = supabase.auth.sign_up(
        {
            "email": email,
            "password": password,
        }
    )

    if response.session is None:
        return False, "Account created. Please verify your email, then login."

    save_auth_session(response, supabase)

    return True, "Account created successfully."


def login_user(email: str, password: str):
    email = email.lower().strip()

    if not email or not password:
        return False, "Please enter email and password."

    supabase = create_supabase_client()

    response = supabase.auth.sign_in_with_password(
        {
            "email": email,
            "password": password,
        }
    )

    save_auth_session(response, supabase)

    return True, "Login successful."


def logout_user():
    supabase = get_supabase()

    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.supabase = create_supabase_client()

    st.rerun()