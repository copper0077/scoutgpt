import os
import json
import logging
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Constants
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = '1wf1_0nORkXoUISggq1dnY5Bnuj9mvwrH9ouiChxwXfU'

# Load service account credentials from environment variable
SERVICE_ACCOUNT_INFO = os.environ.get('SERVICE_ACCOUNT_JSON')

if not SERVICE_ACCOUNT_INFO:
    logging.error("❌ SERVICE_ACCOUNT_JSON environment variable is not set.")
    raise RuntimeError("Missing SERVICE_ACCOUNT_JSON env var")

try:
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(SERVICE_ACCOUNT_INFO), scopes=SCOPES
    )
    logging.info("✅ Service account loaded from environment variable.")
except Exception as e:
    logging.error(f"❌ Failed to load credentials from env: {e}")
    raise

# GET /read
@app.route('/read')
def read():
    tab = request.args.get('tab', 'Sheet1')
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SHEET_ID,
            range=f'{tab}!A1:Z1000'
        ).execute()
        values = result.get('values', [])
    except Exception as e:
        logging.error("❌ Sheets API error: %s", str(e))
        return jsonify({"error": f"Failed to read sheet: {str(e)}"}), 500

    if not values:
        return jsonify({"headers": [], "rows": []})

    headers = values[0]
    rows = [dict(zip(headers, row)) for row in values[1:]]

    return jsonify({"headers": headers, "rows": rows})

# POST /write
@app.route('/write', methods=['POST'])
def write():
    data = request.get_json()
    tab = data.get('tab')
    row_data = data.get('row') or data.get('data')  # ✅ Accept either format

    if not tab or not row_data:
        return jsonify({"error": "Missing 'tab' or 'row/data' in request body"}), 400

    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # Get headers from the sheet
        header_result = sheet.values().get(
            spreadsheetId=SHEET_ID,
            range=f'{tab}!A1:Z1'
        ).execute()
        headers = header_result.get('values', [[]])[0]

        # Create a new row matching header order
        new_row = [row_data.get(h, "") for h in headers]

        # Append the row
        append_result = sheet.values().append(
            spreadsheetId=SHEET_ID,
            range=f'{tab}!A1',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [new_row]}
        ).execute()

        logging.info(f"✅ Appended to {tab}: {new_row}")
        return jsonify({"status": "success", "message": "Row written successfully"}), 200

    except Exception as e:
        logging.error(f"❌ Sheets API error (write): {e}")
        return jsonify({"error": "Failed to write to sheet"}), 500

# Flask entry point
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"🚀 Flask app running on port {port}")
    app.run(host='0.0.0.0', port=port)
