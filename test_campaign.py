"""
Test script to simulate the Campaign page email sending process
"""
import sys
sys.path.insert(0, '.')

from src.database import Lead, LeadStatus, get_session
from src.scheduler import process_initial_outreach

print("=" * 60)
print("TESTING INITIAL OUTREACH EMAIL SENDING")
print("=" * 60)

# Check enriched leads
session = get_session()
enriched_leads = session.query(Lead).filter_by(status=LeadStatus.ENRICHED.value).all()
print(f"\n📊 Found {len(enriched_leads)} enriched leads ready to contact")

if len(enriched_leads) == 0:
    print("\n⚠️  No enriched leads found. Please run the scraper first.")
    session.close()
    sys.exit(0)

# Show sample leads
print("\n📋 Sample leads:")
for lead in enriched_leads[:3]:
    print(f"   - {lead.clinic_name}")
    print(f"     Email: {lead.email}")
    print(f"     Status: {lead.status}")

session.close()

# Try to send emails
print("\n🚀 Attempting to send outreach emails...")
try:
    count = process_initial_outreach()
    print(f"\n✅ SUCCESS! Sent {count} emails")
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   Message: {str(e)}")
    import traceback
    traceback.print_exc()
