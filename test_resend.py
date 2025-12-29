import resend
import sys

# Set API key
resend.api_key = "re_ZKcdttQ6_LJwSyo2raH8yb98oL5EuR1PA"

print("Testing Resend API connection...")
print(f"API Key: {resend.api_key[:10]}...")

try:
    result = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": ["delivered@resend.dev"],
        "subject": "Test from Lead Gen Engine",
        "html": "<p>This is a test email to verify Resend integration</p>"
    })
    print("\n✅ SUCCESS! Email sent successfully")
    print(f"Result: {result}")
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Message: {str(e)}")
    sys.exit(1)
