from datetime import date

from googleapiclient.discovery import build

import config
from pipeline.auth import get_credentials


def _get_service():
    return build("sheets", "v4", credentials=get_credentials())


def read_rate_table() -> dict:
    service = _get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=config.GOOGLE_SPREADSHEET_ID,
        range=f"{config.SHEET_TAB_RATES}!A:C",
    ).execute()

    rows = result.get("values", [])
    rate_table = {}
    for row in rows[1:]:  # skip header
        if len(row) >= 2:
            item = row[0]
            try:
                price = int(row[1].replace(",", ""))
            except (ValueError, IndexError):
                continue
            unit = row[2] if len(row) >= 3 else ""
            rate_table[item] = {"price": price, "unit": unit}

    return rate_table


def append_result_row(
    filename: str,
    proposal_url: str,
    pdf_url: str,
    status: str = "完了",
):
    service = _get_service()
    row = [
        date.today().isoformat(),
        filename,
        proposal_url,
        pdf_url,
        status,
    ]
    service.spreadsheets().values().append(
        spreadsheetId=config.GOOGLE_SPREADSHEET_ID,
        range=f"{config.SHEET_TAB_MANAGEMENT}!A:E",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()
