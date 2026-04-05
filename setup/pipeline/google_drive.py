from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import config

SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_service():
    creds = service_account.Credentials.from_service_account_file(
        config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def upload_pdf(file_path: str, filename: str) -> str:
    service = _get_service()

    file_metadata = {
        "name": filename,
        "parents": [config.GOOGLE_DRIVE_FOLDER_ID],
    }
    media = MediaFileUpload(file_path, mimetype="application/pdf")

    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink",
    ).execute()

    return uploaded.get("webViewLink", f"https://drive.google.com/file/d/{uploaded['id']}/view")
