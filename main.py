from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/read')
def read():
    tab = request.args.get('tab')
    # Replace this with actual Google Sheets integration later
    return jsonify({
        "headers": ["Name", "Email"],
        "rows": [
            {"Name": "Alice", "Email": "alice@example.com"},
            {"Name": "Bob", "Email": "bob@example.com"}
        ]
    })

@app.route('/write', methods=['POST'])
def write():
    data = request.get_json()
    tab = data.get('tab')
    row = data.get('row')
    # Replace this with actual write logic
    return jsonify({"status": "success", "message": f"Row written to {tab}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
