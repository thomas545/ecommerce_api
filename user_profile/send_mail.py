import smtplib
from email.mime.text import MIMEText
from django.conf import settings
from celery import shared_task

url = "http://localhost:2000/"


@shared_task
def send_register_mail(user, key):
    body = """<p>
    Hello from E-commerce!<br><br>

    Confirmation Mail: %s

    You can see more details in this link: %saccount-confirm-email/%s<br><br>

    Thank you from E-commerce! <br><br>
    <p>"""% (user.username, url, key)
    
    subject = "Registeration Mail"
    recipients = [user.email]
    
    try:
        send_email(body, subject, recipients, 'html')
        return "Email Is Sent"
    except Exception as e:
        print("Email not sent ", e)

user_mail = getattr(settings, 'EMAIL_HOST_USER', None)
password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
port = getattr(settings, 'EMAIL_PORT', None)

def send_email(body, subject, recipients, body_type='plain'):
    session = smtplib.SMTP('smtp.gmail.com', port)
    session.starttls()
    session.login(user_mail, password)
    sender = 'thomas@dokkanz.com'
    msg = MIMEText(body, body_type)
    msg['subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    session.sendmail(sender, recipients, msg.as_string())

