import requests
from bs4 import BeautifulSoup
import re
from serpapi import GoogleSearch
from src.database import Lead, LeadStatus, get_session
import streamlit as st

def search_leads(query, api_key):
    params = {
        "engine": "google_maps",
        "q": query,
        "type": "search",
        "api_key": api_key
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    leads = []
    if "local_results" in results:
        for result in results["local_results"]:
            leads.append({
                "name": result.get("title"),
                "clinic_name": result.get("title"),
                "website": result.get("website"),
                "phone": result.get("phone")
            })
    return leads

def extract_email_from_url(url):
    if not url:
        return None
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Simple regex for finding emails
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_regex, response.text)
        
        if emails:
            # Filter out some common false positives if necessary
            return emails[0]
        
        # Try finding in footer or contact page if not found on home page (simplified for now)
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def process_scraping_job(query, serp_api_key):
    session = get_session()
    raw_leads = search_leads(query, serp_api_key)
    
    new_leads_count = 0
    for lead_data in raw_leads:
        # Check if website already exists to avoid duplicates
        existing = session.query(Lead).filter_by(website=lead_data['website']).first()
        if existing:
            continue
            
        lead = Lead(
            name=lead_data['name'],
            clinic_name=lead_data['clinic_name'],
            website=lead_data['website'],
            phone=lead_data['phone'],
            status=LeadStatus.FOUND
        )
        session.add(lead)
        new_leads_count += 1
    
    session.commit()
    return new_leads_count

def enrich_leads():
    session = get_session()
    leads_to_enrich = session.query(Lead).filter_by(status=LeadStatus.FOUND).all()
    
    enriched_count = 0
    for lead in leads_to_enrich:
        email = extract_email_from_url(lead.website)
        if email:
            lead.email = email
            lead.status = LeadStatus.ENRICHED
            enriched_count += 1
        else:
            lead.status = LeadStatus.MISSING_INFO
        
    session.commit()
    return enriched_count
