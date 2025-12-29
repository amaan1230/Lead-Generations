from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from src.database import Lead, LeadStatus, get_session
from src.agent import generate_personalized_email, get_email_body
from src.mailer import send_outreach_email
from src.scheduler import run_scheduler as run_followup_scheduler
from src.secrets_loader import get_secret
import streamlit as st
import os

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for development

# ===== Serve Static Files =====
@app.route('/')
def landing():
    return send_from_directory('static', 'landing.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('static', 'dashboard.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

# ===== API Endpoints =====

@app.route('/api/leads', methods=['GET'])
def get_leads():
    """Get all leads"""
    try:
        session = get_session()
        leads = session.query(Lead).all()
        
        leads_data = [{
            'id': lead.id,
            'clinic_name': lead.clinic_name,
            'website': lead.website,
            'email': lead.email,
            'name': lead.name,
            'status': lead.status,
            'follow_up_count': lead.follow_up_count,
            'last_contacted': lead.last_contacted.isoformat() if lead.last_contacted else None
        } for lead in leads]
        
        session.close()
        return jsonify({'success': True, 'leads': leads_data})
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/preview-email', methods=['POST'])
def preview_email():
    """Generate email preview for a lead"""
    try:
        data = request.json
        lead_id = data.get('lead_id')
        
        if not lead_id:
            return jsonify({'success': False, 'error': 'lead_id required'}), 400
        
        session = get_session()
        lead = session.query(Lead).filter_by(id=lead_id).first()
        
        if not lead:
            session.close()
            return jsonify({'success': False, 'error': 'Lead not found'}), 404
        
        # Generate personalized email
        opening = generate_personalized_email(lead.name, lead.clinic_name)
        subject = f"Question for {lead.clinic_name}"
        body = get_email_body(lead, opening)
        
        session.close()
        return jsonify({
            'success': True,
            'subject': subject,
            'body': body
        })
    except Exception as e:
        print(f"Error generating preview: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send-email', methods=['POST'])
def send_email():
    """Send individual email"""
    try:
        data = request.json
        lead_id = data.get('lead_id')
        subject = data.get('subject')
        body = data.get('body')
        
        if not all([lead_id, subject, body]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        success = send_outreach_email(lead_id, subject, body)
        
        return jsonify({'success': success})
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bulk-preview', methods=['POST'])
def bulk_preview():
    """Generate email previews for all enriched leads"""
    try:
        session = get_session()
        leads = session.query(Lead).filter_by(status=LeadStatus.ENRICHED.value).all()
        
        previews = {}
        for lead in leads:
            opening = generate_personalized_email(lead.name, lead.clinic_name)
            subject = f"Question for {lead.clinic_name}"
            body = get_email_body(lead, opening)
            
            previews[lead.id] = {
                'subject': subject,
                'body': body,
                'lead': {
                    'id': lead.id,
                    'clinic_name': lead.clinic_name,
                    'email': lead.email,
                    'name': lead.name
                }
            }
        
        session.close()
        return jsonify({'success': True, 'previews': previews})
    except Exception as e:
        print(f"Error generating bulk preview: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bulk-send', methods=['POST'])
def bulk_send():
    """Send emails to multiple leads"""
    try:
        data = request.json
        lead_ids = data.get('lead_ids', [])
        
        if not lead_ids:
            return jsonify({'success': False, 'error': 'No leads selected'}), 400
        
        session = get_session()
        sent_count = 0
        failed_count = 0
        
        for lead_id in lead_ids:
            lead = session.query(Lead).filter_by(id=lead_id).first()
            if lead:
                # Generate email
                opening = generate_personalized_email(lead.name, lead.clinic_name)
                subject = f"Question for {lead.clinic_name}"
                body = get_email_body(lead, opening)
                
                # Send email
                if send_outreach_email(lead_id, subject, body):
                    sent_count += 1
                else:
                    failed_count += 1
        
        session.close()
        return jsonify({
            'success': True,
            'sent': sent_count,
            'failed': failed_count
        })
    except Exception as e:
        print(f"Error sending bulk emails: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/run-scheduler', methods=['POST'])
def run_scheduler():
    """Run follow-up scheduler"""
    try:
        run_followup_scheduler()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error running scheduler: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/run-scraper', methods=['POST'])
def run_scraper():
    """Run Google Maps scraper and enrichment"""
    try:
        data = request.json
        query = data.get('query')
        
        if not query:
            return jsonify({'success': False, 'error': 'Query required'}), 400
            
        api_key = get_secret("SERP_API_KEY")
        from src.scraper import process_scraping_job, enrich_leads
        
        # Run scraper
        new_leads = process_scraping_job(query, api_key)
        
        # Run enrichment
        enriched = enrich_leads()
        
        return jsonify({
            'success': True,
            'count': new_leads,
            'enriched': enriched
        })
    except Exception as e:
        print(f"Error running scraper: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    try:
        session = get_session()
        leads = session.query(Lead).all()
        
        # Status counts
        status_counts = {}
        for lead in leads:
            status_counts[lead.status] = status_counts.get(lead.status, 0) + 1
            
        # Daily stats (mocked data based on last_contacted for demo)
        # In a real app, you'd query a separate event log table
        daily_stats = {
            'sent': [0]*7,
            'opened': [0]*7
        }
        
        session.close()
        return jsonify({
            'success': True,
            'status_counts': status_counts,
            'daily_stats': daily_stats
        })
    except Exception as e:
        print(f"Error fetching analytics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== Run Server =====
if __name__ == '__main__':
    print("🚀 Starting Lead Generation API Server...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔌 API Base: http://localhost:5000/api")
    app.run(debug=True, host='0.0.0.0', port=5000)
