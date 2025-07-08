import pyodbc
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import argparse
from datetime import datetime

# === Configuration ===
DB_CONFIG = {
    'driver': 'FreeTDS',        # or 'Adaptive Server Enterprise'
    'server': 'your_sybase_host',
    'port': '5000',             # default Sybase port
    'database': 'your_database',
    'uid': 'your_user',
    'pwd': 'your_password'
}

SMTP_CONFIG = {
    'host': 'smtp.example.com',
    'port': 587,
    'username': 'your_email@example.com',
    'password': 'your_email_password',
    'from': 'your_email@example.com'
}

def get_connection():
    conn_str = (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']},{DB_CONFIG['port']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['uid']};PWD={DB_CONFIG['pwd']}"
    )
    return pyodbc.connect(conn_str)

def run_query(conn, date_param):
    query = f"""
    SELECT * FROM your_table
    WHERE some_date_column = '{date_param}'
    """
    return pd.read_sql(query, conn)

def send_email(to_address, subject, body):
    msg = MIMEText(body, 'plain')
    msg['Subject'] = subject
    msg['From'] = SMTP_CONFIG['from']
    msg['To'] = to_address

    with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
        server.starttls()
        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        server.sendmail(SMTP_CONFIG['from'], to_address, msg.as_string())


def send_email_with_attachment(to_address, subject, body_text, attachment_path):
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = SMTP_CONFIG["from"]
    msg["To"] = to_address

    # Attach plain text body
    msg.attach(MIMEText(body_text, "plain"))

    # Attach the Excel file
    with open(attachment_path, "rb") as f:
        part = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
        msg.attach(part)

    with smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port']) as server:
        server.starttls()
        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        server.sendmail(SMTP_CONFIG['from'], to_address, msg.as_string())

def main(date_str, email_to):
    try:
        conn = get_connection()
        df = run_query(conn, date_str)
        conn.close()

        if df.empty:
            body = f"No records found for date {date_str}."
        else:
            body = df.to_string(index=False)

        send_email(email_to, f"Sybase Query Results for {date_str}", body)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format')
    parser.add_argument('--email', required=True, help='Recipient email address')

    args = parser.parse_args()
    main(args.date, args.email)
