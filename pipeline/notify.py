import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config


def send_notification(
    filename: str,
    proposal_url: str,
    pdf_url: str,
):
    msg = MIMEMultipart()
    msg["From"] = config.GMAIL_ADDRESS
    msg["To"] = config.NOTIFY_TO
    msg["Subject"] = f"[daichi-automation] 企画案・見積書 完了: {filename}"

    body = f"""パイプライン完了しました。

■ ファイル: {filename}

■ 企画案 (Googleドキュメント):
{proposal_url}

■ 見積書 (PDF):
{pdf_url}

確認して問題なければクライアントに転送してください。
"""

    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(config.GMAIL_ADDRESS, config.GMAIL_APP_PASSWORD)
        server.send_message(msg)
