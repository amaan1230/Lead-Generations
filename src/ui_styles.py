import streamlit as st

def apply_ios_style():
    """
    Injects custom CSS to style Streamlit app with an iOS aesthetic.
    Matches the variables and design tokens from static/style.css.
    """
    st.markdown("""
        <style>
        /* Import Inter Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        :root {
            --ios-blue: #007AFF;
            --ios-gray: #F2F2F7;
            --text-primary: #000000;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #F2F2F7;
            border-right: 1px solid rgba(0,0,0,0.05);
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }

        /* Hiding Default Header */
        header[data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }

        /* Buttons (iOS Pill Style) */
        .stButton > button {
            border-radius: 99px;
            background-color: #007AFF;
            color: white;
            font-weight: 600;
            border: none;
            padding: 0.5rem 1.2rem;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background-color: #0062cc;
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
            transform: translateY(-1px);
        }

        /* Input Fields */
        .stTextInput > div > div > input {
            border-radius: 12px;
            background-color: rgba(118, 118, 128, 0.12);
            border: 1px solid transparent;
            color: black;
        }

        .stTextInput > div > div > input:focus {
            background-color: rgba(118, 118, 128, 0.08);
            border-color: #007AFF;
            box-shadow: none;
        }

        /* Dataframes / Tables */
        .stDataFrame {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(0,0,0,0.05);
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            font-weight: 700;
            color: #007AFF;
        }

        /* Expander */
        .streamlit-expanderHeader {
            background-color: white;
            border-radius: 12px;
        }
        
        /* Titles and Headers */
        h1, h2, h3 {
            font-weight: 700;
            letter-spacing: -0.02em;
        }
        
        </style>
    """, unsafe_allow_html=True)
