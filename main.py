import imaplib
import email
import time
import os
import sys
from twilio.rest import Client

# Configuration via variables d'environnement Railway
EMAIL = os.environ.get("EMAIL", "")
PASSWORD = os.environ.get("PASSWORD", "")
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")
TO_NUMBER = os.environ.get("TWILIO_TO_NUMBER", "")

# Validation au demarrage
print("=== Demarrage TradingView -> SMS ===", flush=True)
print(f"EMAIL: {'OUI' if EMAIL else 'NON'}", flush=True)
print(f"PASSWORD: {'OUI' if PASSWORD else 'NON'}", flush=True)
print(f"TWILIO_ACCOUNT_SID: {'OUI' if ACCOUNT_SID else 'NON'}", flush=True)
print(f"TWILIO_AUTH_TOKEN: {'OUI' if AUTH_TOKEN else 'NON'}", flush=True)
print(f"TWILIO_FROM_NUMBER: {'OUI' if FROM_NUMBER else 'NON'}", flush=True)
print(f"TWILIO_TO_NUMBER: {'OUI' if TO_NUMBER else 'NON'}", flush=True)

missing = []
if not EMAIL:
    missing.append("EMAIL")
if not PASSWORD:
    missing.append("PASSWORD")
if not ACCOUNT_SID:
    missing.append("TWILIO_ACCOUNT_SID")
if not AUTH_TOKEN:
    missing.append("TWILIO_AUTH_TOKEN")
if not FROM_NUMBER:
    missing.append("TWILIO_FROM_NUMBER")
if not TO_NUMBER:
    missing.append("TWILIO_TO_NUMBER")

if missing:
    print(f"ERREUR: Variables manquantes: {', '.join(missing)}", flush=True)
    sys.exit(1)

clean_password = PASSWORD.replace(" ", "")
print(f"Password longueur: {len(clean_password)} chars", flush=True)

# Client Twilio
try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    print("Twilio client OK", flush=True)
except Exception as e:
    print(f"ERREUR Twilio: {e}", flush=True)
    sys.exit(1)


def send_sms(message):
    try:
        msg = client.messages.create(
            body=message,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        print(f"SMS envoye OK (SID: {msg.sid}): {message}", flush=True)
        return True
    except Exception as e:
        print(f"ERREUR envoi SMS: {e}", flush=True)
        return False


def check_email():
    mail = None
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(EMAIL, clean_password)
        print("Connexion Gmail OK", flush=True)
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')
        if status != "OK":
            print(f"Erreur recherche: {status}", flush=True)
            return

        email_ids = messages[0].split()
        if not email_ids:
            print("Aucun nouvel email", flush=True)
            return

        print(f"{len(email_ids)} nouvel(s) email(s)", flush=True)
        for e_id in email_ids:
            try:
                _, msg_data = mail.fetch(e_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                subject = msg.get("subject", "(sans sujet)")
                sender = msg.get("from", "inconnu")
                print(f"Email de: {sender} | Sujet: {subject}", flush=True)
                send_sms(f"TradingView: {subject}")
                mail.store(e_id, '+FLAGS', '\\Seen')
            except Exception as e:
                print(f"Erreur email {e_id}: {e}", flush=True)

    except imaplib.IMAP4.error as e:
        print(f"ERREUR IMAP auth: {e}", flush=True)
        print("Verifiez que vous utilisez un App Password Gmail (16 chars)", flush=True)
    except Exception as e:
        print(f"ERREUR check_email: {e}", flush=True)
    finally:
        if mail:
            try:
                mail.logout()
            except:
                pass


# Boucle principale
print("Surveillance emails toutes les 30s...", flush=True)
cycle = 0
while True:
    cycle += 1
    print(f"--- Cycle #{cycle} ---", flush=True)
    check_email()
    time.sleep(30)
