import streamlit as st
from src.ui_styles import apply_ios_style
import pandas as pd
from src.database import Lead, get_session
from sqlalchemy import func

st.set_page_config(page_title="Outreach Engine Dashboard", layout="wide")
apply_ios_style()

st.title("🚀 Lead Gen & Outreach Engine")

def get_stats():
    session = get_session()
    stats = session.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
    session.close()
    return dict(stats)

stats = get_stats()

st.subheader("High-Level Overview")
cols = st.columns(len(stats) if stats else 1)

if not stats:
    st.info("No leads found yet. Head over to the Scraper page to start!")
else:
    for i, (status, count) in enumerate(stats.items()):
        cols[i % len(cols)].metric(status, count)

st.divider()

st.subheader("Recent Activity")
session = get_session()
recent_leads = session.query(Lead).order_by(Lead.created_at.desc()).limit(10).all()
if recent_leads:
    df = pd.DataFrame([{
        "Clinic Name": l.clinic_name,
        "Status": l.status,
        "Email": l.email,
        "Last Contacted": l.last_contacted,
        "Created At": l.created_at
    } for l in recent_leads])
    st.table(df)
else:
    st.write("No recent activity.")
session.close()

st.sidebar.success("Select a page above.")
