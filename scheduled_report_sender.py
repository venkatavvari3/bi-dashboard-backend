import os
import sys
import logging
import psycopg2
import smtplib
import jwt
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Ensure stdout is line-buffered for GitHub Actions
sys.stdout.reconfigure(line_buffering=True)

# Configure logging to output to console with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logging.info("Starting scheduled report sender script...")

# Load environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SECRET = os.getenv("SECRET", "CHANGE_ME")

try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Get current time
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_day = now.strftime("%A")
    current_day_of_month = now.day

    # Fetch subscriptions matching the current time
    cur.execute("SELECT email, repeat_frequency FROM subscriptions WHERE scheduled_time = %s", (current_time,))
    #cur.execute("SELECT email, repeat_frequency FROM subscriptions")
    subscriptions = cur.fetchall()
    logging.info(f"Found {len(subscriptions)} subscriptions scheduled for {current_time}")

    # Function to determine if a report should be sent today
    def should_send_today(frequency):
        if frequency.lower() == "daily":
            return True
        elif frequency.lower() == "weekly":
            return current_day == "Monday"
        elif frequency.lower() == "monthly":
            return current_day_of_month == 1
        return False

    # Send emails
    for email, frequency in subscriptions:
        if should_send_today(frequency):
            token = jwt.encode({"sub": email}, SECRET, algorithm="HS256")
            login_url = f"https://bi-dashboard-frontend.vercel.app/?token={token}"

            msg = MIMEMultipart()
            msg["Subject"] = "Your Scheduled BI Dashboard Report"
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = email
            body = f"Hello,\n\nClick the link below to access your dashboard:\n{login_url}\n\nThis link logs you in automatically.\n\nRegards,\nBI Dashboard"
            msg.attach(MIMEText(body, "plain"))

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    smtp.sendmail(EMAIL_ADDRESS, [email], msg.as_string())
                logging.info(f"Email sent to {email}")
            except Exception as e:
                logging.error(f"Failed to send email to {email}: {e}")

    cur.close()
    conn.close()
    logging.info("Scheduled report sender script completed.")

except Exception as e:
    logging.error(f"Script failed due to error: {e}")
