import streamlit as st
from src.ui_styles import apply_ios_style
import pandas as pd
import plotly.express as px
from src.database import Lead, get_session
from sqlalchemy import func

st.set_page_config(page_title="Outreach Analytics", page_icon="📊", layout="wide")
apply_ios_style()

st.title("📊 Outreach Analytics")

session = get_session()

# Status Distribution
status_counts = session.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
if status_counts:
    df_status = pd.DataFrame(status_counts, columns=['Status', 'Count'])
    fig = px.pie(df_status, values='Count', names='Status', title="Lead Status Distribution")
    st.plotly_chart(fig)
    
    # Conversion Rate
    total = sum(d[1] for d in status_counts)
    contacted = sum(d[1] for d in status_counts if d[0] in ['Contacted', 'Followup_1', 'Followup_2', 'Followup_3', 'Replied'])
    replied = sum(d[1] for d in status_counts if d[0] == 'Replied')
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Leads", total)
    col2.metric("Reach Rate", f"{contacted/total*100:.1f}%" if total > 0 else "0%")
    col3.metric("Reply Rate", f"{replied/contacted*100:.1f}%" if contacted > 0 else "0%")
else:
    st.info("No data available for analytics.")

session.close()
