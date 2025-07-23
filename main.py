import os
import logging
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = 'wf1_0nORkXoUISggq1dnY5Bnuj9mvwrH9ouiChxwXfU'
SERVICE_ACCOUNT_FILE = '/Service_Account_Secret/service-account.json'  # ✅ FIXED path

try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    logging.info("✅ Service account loaded.")
except Exception as e:
    logging.error(f"❌ Failed to load credentials: {e}")
    raise

@app.route('/read')
def read():
    tab = request.args.get('tab', 'Sheet1')
    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()
        range_name = f'{tab}!A1:Z1000'
        result = sheet.values().get(spreadsheetId=SHEET_ID, range=range_name).execute()
        values = result.get('values', [])
    except Exception as e:
        logging.error(f"❌ Sheets API error: {e}")
        return jsonify({"error": "Failed to read sheet"}), 500

    if not values:
        return jsonify({"headers": [], "rows": []})

    headers = values[0]
    rows = [dict(zip(headers, row)) for row in values[1:]]

    return jsonify({"headers": headers, "rows": rows})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logging.info(f"🚀 Flask app running on port {port}")
    app.run(host='0.0.0.0', port=port)
