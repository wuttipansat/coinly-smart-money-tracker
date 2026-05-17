import streamlit as st
from supabase import create_client, Client

def create_supabase_client() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_ANON_KEY"]
    )

def get_supabase() -> Client:
    if "supabase" not in st.session_state:
        st.session_state.supabase = create_supabase_client()

    return st.session_state.supabase