import os
import sys
import logging
import psycopg2
import smtplib
import jwt
import base64
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import time

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
    cur.execute("SELECT email, repeat_frequency, report_format FROM subscriptions WHERE scheduled_time = %s", (current_time,))
    #cur.execute("SELECT email, repeat_frequency, report_format FROM subscriptions")
    subscriptions = cur.fetchall()
    logging.info(f"Found {subscriptions} subscriptions")
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

    # Function to generate report files from dashboard
    def generate_report_files(login_url, report_format):
        """
        Generate PDF and/or Excel files from the dashboard URL
        Returns a dictionary with generated files as base64 strings
        
        TODO: Implement actual report generation using:
        - Playwright/Selenium for browser automation
        - Navigate to login_url and wait for dashboard to load
        - Use browser's print to PDF feature for PDF generation
        - Export data tables to Excel format
        - Return actual binary file data
        """
        attachments = {}
        
        try:
            logging.info(f"Generating reports for format: {report_format}")
            
            if 'pdf' in report_format.lower() or 'both' in report_format.lower():
                # Simulate PDF generation - Replace with actual implementation
                logging.info("Generating PDF report...")
                # TODO: Use headless browser to:
                # 1. Navigate to login_url
                # 2. Wait for dashboard to fully load
                # 3. Use page.pdf() to generate PDF
                # 4. Return binary PDF data
                
                # Temporary simulation
                pdf_content = f"BI Dashboard Report\nGenerated: {datetime.now()}\nAccess URL: {login_url}\n\n[Dashboard content would be here]"
                attachments['pdf'] = base64.b64encode(pdf_content.encode()).decode()
                logging.info("PDF report generated successfully")
                
            if 'excel' in report_format.lower() or 'both' in report_format.lower():
                # Simulate Excel generation - Replace with actual implementation
                logging.info("Generating Excel report...")
                # TODO: Use headless browser to:
                # 1. Navigate to login_url
                # 2. Extract data from dashboard tables/charts
                # 3. Use pandas/openpyxl to create Excel file
                # 4. Return binary Excel data
                
                # Temporary simulation
                excel_content = f"Report Type,Value,Timestamp\nDashboard Report,Generated,{datetime.now()}\nAccess URL,{login_url},N/A"
                attachments['excel'] = base64.b64encode(excel_content.encode()).decode()
                logging.info("Excel report generated successfully")
                
        except Exception as e:
            logging.error(f"Failed to generate reports: {e}")
            
        return attachments

    # Send emails
    for email, frequency, report_format in subscriptions:
        if should_send_today(frequency):
            token = jwt.encode({"sub": email}, SECRET, algorithm="HS256")
            login_url = f"https://bi-dashboard-frontend.vercel.app/?token={token}"

            # Generate report files based on format
            attachments = generate_report_files(login_url, report_format)

            msg = MIMEMultipart()
            msg["Subject"] = "Your Scheduled BI Dashboard Report"
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = email
            
            # Create email body
            attachment_info = ""
            if attachments:
                formats = []
                if 'pdf' in attachments:
                    formats.append("PDF")
                if 'excel' in attachments:
                    formats.append("Excel")
                attachment_info = f"\n\nAttached: {', '.join(formats)} report(s)"
            
            body = f"Hello,\n\nYour scheduled BI Dashboard report is ready!{attachment_info}\n\nClick the link below to access your live dashboard:\n{login_url}\n\nThis link logs you in automatically.\n\nRegards,\nBI Dashboard Team"
            msg.attach(MIMEText(body, "plain"))

            # Add PDF attachment if generated
            if 'pdf' in attachments:
                try:
                    pdf_data = base64.b64decode(attachments['pdf'])
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(pdf_data)
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="dashboard_report_{now.strftime("%Y%m%d_%H%M")}.pdf"'
                    )
                    part.add_header("Content-Type", "application/pdf")
                    msg.attach(part)
                    logging.info(f"PDF attachment added for {email}")
                except Exception as e:
                    logging.error(f"Failed to attach PDF for {email}: {e}")

            # Add Excel attachment if generated
            if 'excel' in attachments:
                try:
                    excel_data = base64.b64decode(attachments['excel'])
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(excel_data)
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f'attachment; filename="dashboard_data_{now.strftime("%Y%m%d_%H%M")}.xlsx"'
                    )
                    part.add_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    msg.attach(part)
                    logging.info(f"Excel attachment added for {email}")
                except Exception as e:
                    logging.error(f"Failed to attach Excel for {email}: {e}")

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                    smtp.sendmail(EMAIL_ADDRESS, [email], msg.as_string())
                logging.info(f"Email sent to {email} with format: {report_format}")
            except Exception as e:
                logging.error(f"Failed to send email to {email}: {e}")

    cur.close()
    conn.close()
    logging.info("Scheduled report sender script completed.")

except Exception as e:
    logging.error(f"Script failed due to error: {e}")
