# 🚀 LeadGen & Automated Outreach Engine

A powerful, all-in-one platform for B2B lead generation, AI-driven enrichment, and automated email outreach. Built with a modern **iOS-style** interface for a premium user experience.

![Dashboard Preview](static/dashboard_preview.png)

## ✨ Features

### 1. 🔍 Smart Lead Scraping
- **Google Maps Integration**: Instantly find businesses by keyword (e.g., "Dentists in New York").
- **Data Extraction**: Automatically captures business names, websites, phone numbers, and addresses.

### 2. 🧠 AI Enrichment & Personalization
- **Website Analysis**: The AI agent visits prospect websites to understand their services and value proposition.
- **Hyper-Personalized Emails**: Generates unique opening lines for every single lead, drastically increasing reply rates.
- **Email Finder**: Identifies valid contact emails for the business.

### 3. 📧 Automated Outreach Campaigns
- **One-Click Sending**: Review AI-drafted emails and send them individually or in bulk.
- **Auto-Followups**: Intelligent scheduler tracks non-responders and sends follow-up sequences automatically.
- **SMTP Support**: Connects to your own email provider for high deliverability.

### 4. 📊 Real-Time Analytics
- **Live Dashboard**: Track total leads, emails sent, open rates, and replies.
- **Visual Charts**: Interactive graphs powered by Plotly to visualize campaign performance.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask (API), SQLite (Database)
- **Frontend**: Streamlit (App), HTML/CSS (Landing Page)
- **AI Engine**: Google Gemini / OpenAI (configurable)
- **Styling**: Custom CSS with Glassmorphism & iOS Design System

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+ installed
- A Google Cloud API Key (for Gemini) or OpenAI Key
- SerpAPI Key (for Google Maps scraping)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/amaan1230/Lead-Generations.git
    cd Lead-Generations
    ```

2.  **Set up Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Secrets**
    Create a `.env` file or `secrets.toml` in `.streamlit/` with your keys:
    ```toml
    SERP_API_KEY = "your_key"
    GEMINI_API_KEY = "your_key"
    EMAIL_ADDRESS = "your_email"
    EMAIL_PASSWORD = "your_app_password"
    ```

### Running the App

**Option 1: Full Dashboard (Streamlit)**
```bash
streamlit run app.py
```

**Option 2: Landing Page (Flask)**
```bash
python api.py
```
Visit `http://localhost:5000` to see the landing page.

---

## 📸 Screenshots

### Landing Page
_Modern, high-converting landing page included._

### Campaign Manager
_Review and edit AI-generated emails before sending._

---

## 📄 License
This project is licensed under the MIT License.
