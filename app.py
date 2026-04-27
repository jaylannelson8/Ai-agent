from flask import Flask, request, jsonify, render_template
from config import Config
from business import analyze_tick
import os

app = Flask(__name__)

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    # Return 200 so the Mothership knows the site is up
    return jsonify({"result": "success", "message": "Azure Cloud Live"}), 200

@app.route('/tick/<tick_id>', methods=['POST'])
def tick(tick_id):
    # Verify API Key from headers
    auth = request.headers.get("apikey") or request.headers.get("x-api-key")
    if auth != Config.API_KEY:
        return jsonify({"result": "failure", "message": "Unauthorized"}), 401
    
    data = request.get_json(silent=True, force=True)
    result = analyze_tick(data, tick_id)
    
    # status_code 200 for success, 400 for errors
    status_code = 200 if result.get("result") == "success" else 400
    return jsonify(result), status_code

@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Public dashboard (vibrant template)
    return render_template("dashboard.html", positions=[], history=[])

if __name__ == '__main__':
    # Azure provides the PORT environment variable. Fallback to 5345 for local testing.
    port = int(os.environ.get("PORT", 5345))
    app.run(host='0.0.0.0', port=port)