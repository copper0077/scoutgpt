import os
from flask import Flask, request, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = 'wf1_0nORkXoUISggq1dnY5Bnuj9mvwrH9ouiChxwXfU'
SERVICE_ACCOUNT_FILE = '/secrets/Service_Account_Secret.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

@app.route('/read')
def read():
    tab = request.args.get('tab')
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    range_name = f'{tab}!A1:Z1000'
    result = sheet.values().get(spreadsheetId=SHEET_ID, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        return jsonify({"headers": [], "rows": []})

    headers = values[0]
    rows = [dict(zip(headers, row)) for row in values[1:]]

    return jsonify({"headers": headers, "rows": rows})

# ✅ Start the Flask app (required for Cloud Run)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
