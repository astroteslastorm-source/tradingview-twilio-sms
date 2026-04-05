import imaplib
import email
import time
import os
import sys
from twilio.rest import Client

# ============================================================
# CONFIGURATION - Variables d'environnement Railway
# IMPORTANT: PASSWORD doit etre un App Password Gmail (16 chars)
# Generer sur: https://myaccount.google.com/apppasswords
# ============================================================
EMAIL = os.environ.get("EMAIL", "")
PASSWORD = os.environ.get("PASSWORD", "")
ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
FROM_NUMBER = os.environ.get("TWILIO_FROM_NUMBER", "")
TO_NUMBER = os.environ.get("TWILIO_TO_NUMBER", "")

# ============================================================
# VALIDATION AU DEMARRAGE
# ============================================================
print("=== Demarrage TradingView -> SMS ===", flush=True)
print(f"EMAIL configure: {'OUI' if EMAIL else 'NON - manquant!'}", flush=True)
print(f"PASSWORD configure: {'OUI' if PASSWORD else 'NON - manquant!'}", flush=True)
print(f"TWILIO_ACCOUNT_SID configure: {'OUI' if ACCOUNT_SID else 'NON - manquant!'}", flush=True)
print(f"TWILIO_AUTH_TOKEN configure: {'OUI' if AUTH_TOKEN else 'NON - manquant!'}", flush=True)
print(f"FROM_NUMBER configure: {'OUI' if FROM_NUMBER else 'NON - manquant!'}", flush=True)
print(f"TO_NUMBER configure: {'OUI' if TO_NUMBER else 'NON - manquant!'}", flush=True)

missing = []
if not EMAIL: missing.append("EMAIL")
    if not PASSWORD: missing.append("PASSWORD")
        if not ACCOUNT_SID: missing.append("TWILIO_ACCOUNT_SID")
            if not AUTH_TOKEN: missing.append("TWILIO_AUTH_TOKEN")
                if not FROM_NUMBER: missing.append("TWILIO_FROM_NUMBER")
                    if not TO_NUMBER: missing.append("TWILIO_TO_NUMBER")

if missing:
        print(f"ERREUR FATALE: Variables manquantes: {', '.join(missing)}", flush=True)
        print("Verifiez vos variables d'environnement dans Railway > Variables", flush=True)
        sys.exit(1)

# Validation longueur App Password Gmail (doit etre 16 chars sans espaces)
clean_password = PASSWORD.replace(" ", "")
if len(clean_password) == 16:
        print("INFO: App Password Gmail detecte (16 chars) - OK", flush=True)
else:
        print(f"AVERTISSEMENT: PASSWORD a {len(clean_password)} chars (attendu 16 pour App Password)", flush=True)
        print("RAPPEL: Utilisez un App Password Gmail, pas votre mot de passe normal!", flush=True)

# ============================================================
# CLIENT TWILIO
# ============================================================
try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        print("Twilio client initialise avec succes", flush=True)
except Exception as e:
        print(f"ERREUR Twilio init: {e}", flush=True)
        sys.exit(1)

# ============================================================
# FONCTIONS
# ============================================================
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
                        print(f"Erreur recherche emails: {status}", flush=True)
                        return

        email_ids = messages[0].split()
        if not email_ids:
                        print("Aucun nouvel email", flush=True)
                        return

        print(f"{len(email_ids)} nouvel(s) email(s) trouve(s)", flush=True)
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
                print(f"Erreur traitement email {e_id}: {e}", flush=True)

except imaplib.IMAP4.error as e:
        error_msg = str(e)
        if "Application-specific password" in error_msg or "APPSPECIFIC" in error_msg:
                        print("ERREUR AUTH: App Password Gmail requis!", flush=True)
                        print("1. Activez 2FA sur votre compte Google", flush=True)
                        print("2. Allez sur https://myaccount.google.com/apppasswords", flush=True)
                        print("3. Creez un App Password pour 'Mail'", flush=True)
                        print("4. Mettez ce mot de passe 16 chars dans la variable PASSWORD de Railway", flush=True)
elif "Invalid credentials" in error_msg:
                print("ERREUR AUTH: Identifiants invalides", flush=True)
                print("Verifiez EMAIL et PASSWORD dans Railway > Variables", flush=True)
else:
                print(f"ERREUR IMAP: {e}", flush=True)
except Exception as e:
        print(f"ERREUR check_email: {e}", flush=True)
finally:
        if mail:
                        try:
                                            mail.logout()
                                        except:
                pass

# ============================================================
# BOUCLE PRINCIPALE
# ============================================================
print("Demarrage boucle de surveillance emails (toutes les 30s)...", flush=True)
cycle = 0
while True:
        cycle += 1
    print(f"--- Cycle #{cycle} ---", flush=True)
    check_email()
    time.sleep(30)
