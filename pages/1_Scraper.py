import streamlit as st
from src.ui_styles import apply_ios_style
from src.scraper import process_scraping_job, enrich_leads
from src.database import get_session, Lead

st.set_page_config(page_title="Clinic Scraper", page_icon="🔍")
apply_ios_style()
st.title("🔍 Clinic Scraper")

with st.form("scraper_form"):
    query = st.text_input("Search Query (e.g. 'Dental clinics in New York')", value="Dental clinics in New York")
    submit = st.form_submit_button("Start Scraping")

if submit:
    try:
        serp_api_key = st.secrets["SERP_API_KEY"]
        with st.spinner("Scraping leads from Google Maps..."):
            count = process_scraping_job(query, serp_api_key)
            st.success(f"Found {count} new leads!")
            
        with st.spinner("Enriching leads with emails..."):
            enriched = enrich_leads()
            st.success(f"Enriched {enriched} leads with emails!")
            
    except KeyError:
        st.error("Missing SERP_API_KEY in st.secrets")

st.divider()

st.subheader("Scraping History")
session = get_session()
leads = session.query(Lead).all()
if leads:
    st.write(f"Total leads in database: {len(leads)}")
    if st.button("Clear Database"):
        session.query(Lead).delete()
        session.commit()
        st.rerun()
session.close()
