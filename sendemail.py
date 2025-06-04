import os
import smtplib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

SUBJECT = "Expense Tracker Notification"

# Load credentials from environment
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

def sendmail(text, recipient_email):
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(EMAIL_USER, EMAIL_PASS)
            message = f"Subject: {SUBJECT}\n\n{text}"
            s.sendmail(EMAIL_USER, recipient_email, message)
        print(f"Email sent to {recipient_email} via SMTP")
    except Exception as e:
        print(f"SMTP email error: {e}")

def sendgridmail(text, recipient_email):
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        message = Mail(
            from_email=EMAIL_USER,
            to_emails=recipient_email,
            subject=SUBJECT,
            plain_text_content=text
        )
        response = sg.send(message)
        print(f"SendGrid email sent, status code: {response.status_code}")
    except Exception as e:
        print(f"SendGrid email error: {e}")
