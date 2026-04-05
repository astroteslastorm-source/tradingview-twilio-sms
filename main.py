import imaplib
import email
import time
import os
from twilio.rest import Client

# Gmail
EMAIL = os.environ.get("EMAIL", "tradeorage100@gmail.com")
PASSWORD = os.environ.get("PASSWORD", "67@Rbol!R")

# Twilio
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "AC1c9727b1d5a143d2a0ff83ccb3ed59bf")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "0b14b220cc478e7cb72278a14422c859")
FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "+16624384894")
TO_NUMBER = os.environ.get("TWILIO_TO_NUMBER", "+14388607279")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

print("Demarrage du programme email -> SMS", flush=True)
print(f"Surveillance de: {EMAIL}", flush=True)
print(f"SMS vers: {TO_NUMBER}", flush=True)

def send_sms(message):
        client.messages.create(
                    body=message,
                    from_=FROM_NUMBER,
                    to=TO_NUMBER
        )
        print(f"SMS envoye: {message}", flush=True)

def check_email():
        print("Connexion IMAP Gmail...", flush=True)
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        print("Connexion reussie. Recherche emails non lus de TradingView...", flush=True)

    status, messages = mail.search(None, 'UNSEEN FROM "noreply@tradingview.com"')
    email_ids = messages[0].split()
    print(f"Emails trouves: {len(email_ids)}", flush=True)

    for e_id in email_ids:
                _, msg_data = mail.fetch(e_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                subject = msg["subject"]
                print(f"Traitement email: {subject}", flush=True)
                send_sms(f"TradingView: {subject}")
                mail.store(e_id, '+FLAGS', '\\Seen')

    mail.logout()

while True:
        try:
                    check_email()
except Exception as e:
        print(f"Erreur: {e}", flush=True)
    time.sleep(60)
