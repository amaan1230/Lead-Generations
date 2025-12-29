import os
import toml
import streamlit as st
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

def get_secret(key, default=None):
    """
    Retrieve a secret/config value from:
    1. Streamlit secrets (if available and running in Streamlit)
    2. Environment variables
    3. secrets.toml file (manually loaded if Streamlit is not active)
    4. Default value
    """
    
    # 1. Try Streamlit secrets (only works if running via `streamlit run`)
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass  # Streamlit might not be initialized

    # 2. Try Environment Variables
    if key in os.environ:
        return os.environ[key]

    # 3. Try manual loading of secrets.toml (for Flask/Standalone)
    secrets_path = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            secrets = toml.load(secrets_path)
            if key in secrets:
                return secrets[key]
        except Exception:
            pass
            
    return default
