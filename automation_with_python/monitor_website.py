import requests
import smtplib
import os

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

url = 'http://13.60.54.210:8080/'

def send_email_notification(email_msg):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        msg = f"Subject: SITE DOWN\n{email_msg}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)


try:
    response = requests.get(url)
    if response.status_code == 200:
        print("Application is up and running!")
    else:
        print("Application is down! Fix it!")
        # send email
        msg = "Application returned status{response.status_code}. Fix the issue!"
        send_email_notification(msg)
except Exception as ex:
    print(f'Connection error happened: {ex}')
    msg = f"Application Not Accessible Fix the issue!"
    send_email_notification(msg)


