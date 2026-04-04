from google.oauth2 import service_account
from googleapiclient.discovery import build

import config

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]


def _get_services():
    creds = service_account.Credentials.from_service_account_file(
        config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    docs = build("docs", "v1", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    return docs, drive


def create_proposal_doc(proposals: dict, filename: str) -> str:
    docs, drive = _get_services()

    title = f"企画案 - {filename}"
    doc = docs.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    # Move to the target Drive folder
    drive.files().update(
        fileId=doc_id,
        addParents=config.GOOGLE_DRIVE_FOLDER_ID,
        removeParents="root",
        fields="id, parents",
    ).execute()

    # Build document content (insert in reverse order since index shifts)
    requests = []
    insert_index = 1

    for i, proposal in enumerate(proposals["proposals"]):
        sections = []

        # Title
        sections.append(f"企画案{i + 1}: {proposal['title']}\n")
        sections.append(f"\n【コンセプト】\n{proposal['concept']}\n")
        sections.append(f"\n【ターゲット】\n{proposal['target_audience']}\n")
        sections.append(f"\n【トーン】\n{proposal['tone']}\n")
        sections.append(f"\n【想定尺】\n{proposal['duration_seconds']}秒\n")

        # Key messages
        messages = "\n".join(f"  ・{m}" for m in proposal["key_messages"])
        sections.append(f"\n【伝えたいメッセージ】\n{messages}\n")

        # Scenes
        sections.append("\n【構成】\n")
        for scene in proposal["scenes"]:
            sections.append(
                f"  Scene {scene['scene_number']} ({scene['duration_seconds']}秒): "
                f"{scene['description']}\n"
                f"    → 映像: {scene['visual_notes']}\n"
            )

        if i < len(proposals["proposals"]) - 1:
            sections.append("\n" + "=" * 50 + "\n\n")

        text = "".join(sections)
        requests.append({
            "insertText": {"location": {"index": insert_index}, "text": text}
        })
        insert_index += len(text)

    if requests:
        docs.documents().batchUpdate(
            documentId=doc_id, body={"requests": requests}
        ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"
