import os
import sys
import django
import time
import smtplib
from django.utils import timezone  # Add this import at the top
from email.mime.text import MIMEText


# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TimeVaultProject.settings")
django.setup()

# Import your model after setting up Django
from vaultapp.models import Letter


# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "yourthoughtsmatter87@gmail.com"  # Replace with your actual email
EMAIL_PASSWORD = "iamb tyxx ivvj zczs"  # Replace with your Gmail App Password


# Function to send email
def send_email(recipient_email, subject, body):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

            # Prepare email message
            message = MIMEText(body)
            message["Subject"] = subject
            message["From"] = EMAIL_ADDRESS
            message["To"] = recipient_email

            # Send the email
            server.sendmail(EMAIL_ADDRESS, [recipient_email], message.as_string())
            print(f"Email sent successfully to: {recipient_email}")
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {e}")

# Main scheduler loop
def scheduler():
    while True:
        now = timezone.now()
        
        scheduled_letters = Letter.objects.filter(send_date__lte=now, status="scheduled").order_by('-priority', 'send_date')


        # Now process the sorted letters
        for letter in scheduled_letters:
            print(f"Attempting to send email to {letter.recipient_email}")
            send_email(
                recipient_email=letter.recipient_email,
                subject="Your Scheduled Letter",
                body=letter.content,
            )

            # Update the status of the letter after attempting to send
            letter.status = "sent"
            letter.save()
            print(f"Email status updated to 'sent' for: {letter.recipient_email}")

        # Wait for a minute before checking the database again
        time.sleep(60)

# Run the scheduler
if __name__ == "__main__":
    print("Starting scheduler...")
    scheduler()


# import os
# import sys
# import django
# import time
# import smtplib
# from datetime import datetime
# from email.mime.text import MIMEText

# # Set up Django environment
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TimeVaultProject.settings")
# django.setup()

# # Import your model after setting up Django
# from vaultapp.models import Letter


# # SMTP Configuration
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587
# EMAIL_ADDRESS = "yourthoughtsmatter87@gmail.com"  # Replace with your email
# EMAIL_PASSWORD = "iamb tyxx ivvj zczs"  # Use App Password if you're using Gmail


# # Function to send email
# def send_email(recipient_email, subject, body):
#     try:
#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()  # Secure the connection
#             server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

#             # Prepare email message
#             message = MIMEText(body)
#             message["Subject"] = subject
#             message["From"] = EMAIL_ADDRESS
#             message["To"] = recipient_email

#             # Send the email
#             server.sendmail(EMAIL_ADDRESS, [recipient_email], message.as_string())
#             print(f"Email sent successfully to: {recipient_email}")
#     except Exception as e:
#         print(f"Failed to send email to {recipient_email}: {e}")


# # Main scheduler loop
# def custom_priority(letter):
#     priority_map = {'low': 0, 'medium': 1, 'high': 2}  # Mapping of priority
#     return priority_map.get(letter.priority, 0)  # Default to 'low' if invalid
# def scheduler():
#     while True:
#         now = datetime.now()
#         # Fetch all scheduled letters that should be sent at or before the current time
#         # Ensure timezone-aware dates if using Django's timezone
#         # scheduled_letters = Letter.objects.filter(send_date__lte=now, status="scheduled")
#         scheduled_letters = Letter.objects.filter(send_date__lte=now, status="scheduled").order_by('-priority', 'send_date')

#         for letter in scheduled_letters:
#             # Send email using the defined function
#             print(f"Attempting to send email to {letter.recipient_email}")
#             send_email(
#                 recipient_email=letter.recipient_email,
#                 subject="Your Scheduled Letter",
#                 body=letter.content,
#             )

#             # Update the status of the letter after attempting to send
#             letter.status = "sent"
#             letter.save()
#             print(f"Email status updated to 'sent' for: {letter.recipient_email}")

#         # Wait for a minute before checking the database again
#         time.sleep(60)


# # Run the scheduler
# if __name__ == "__main__":
#     print("Starting scheduler...")
#     scheduler()
