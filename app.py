import json
from flask import Flask, render_template, jsonify, request
from datetime import datetime
from pymongo import MongoClient
import os

# --- MongoDB Configuration ---
MONGO_URI = "mongodb+srv://student:student@cluster0.tt1v1.mongodb.net/"
DB_NAME = "people_counting"
COLLECTION_NAME = "full_json_data"
DOCUMENT_ID = "full_dashboard_data"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# --- Configuration ---
HALL_CONFIG = {
    "hall_1": "rtsp://user:bitsathy123@10.10.133.22",
    "hall_2": "rtsp://gopal:bitsathy%40123@10.10.131.30",
    "hall_3": "rtsp://gopal:bitsathy%40123@10.10.131.10"
}
TEMPLATE_FILE = "dashboard.html"

app = Flask(__name__, template_folder='.')


@app.route('/')
def index():
    """Renders the main dashboard page."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    return render_template(TEMPLATE_FILE, hall_names=list(HALL_CONFIG.keys()), today_date=today_str)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})


@app.route('/api/data')
def api_data():
    """API endpoint that returns analytics data from MongoDB for a given date."""
    try:
        # Fetch full JSON document from MongoDB
        doc = collection.find_one({"_id": DOCUMENT_ID})
        data = doc.get("data", {}) if doc else {}
    except Exception as e:
        print(f"[❌] MongoDB read error: {e}")
        data = {}

    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    daily_data_all_streams = data.get(date_str, {})

    overall_in = 0
    overall_out = 0
    individual_counts = {}

    hall_names = list(HALL_CONFIG.keys())

    for i, hall_name in enumerate(hall_names):
        stream_key = f"stream_{i}"
        stream_data = daily_data_all_streams.get(stream_key, {
            "in_count": 0,
            "out_count": 0
        })

        individual_counts[hall_name] = stream_data
        overall_in += stream_data.get("in_count", 0)
        overall_out += stream_data.get("out_count", 0)

    response_data = {
        "overall": {
            "in_count": overall_in,
            "out_count": overall_out
        },
        "halls": individual_counts
    }

    return jsonify(response_data)


if __name__ == '__main__':
    print(f"[INFO] Starting Flask data server at http://0.0.0.0:5002")
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

