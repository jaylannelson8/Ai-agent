import json
import requests
import csv
import os
from config import Config
from ai_logic import get_trading_recommendation

HISTORY_FILE = "history.csv"
POSITIONS_FILE = "positions.json"
MOTHERSHIP_URL = "https://mothership-crg7hzedd6ckfegv.eastus-01.azurewebsites.net/make_trade"

def analyze_tick(payload, tick_id):
    # 1. Sync Positions
    positions = payload.get("Positions") or payload.get("positions") or []
    with open(POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=4)

    # 2. Get AI Recommendations
    ai_raw_json = get_trading_recommendation(payload)
    trades = []
    try:
        ai_data = json.loads(ai_raw_json)
        trades = ai_data.get("trades", [])
    except:
        trades = []

    # 3. FIX: Hard-Validation for Ticker as String
    market_data = payload.get("Market_Summary") or payload.get("market_summary") or []
    
    if not trades or not isinstance(trades, list) or len(trades) == 0:
        if market_data:
            # Force the ticker to be a string using str()
            valid_ticker = str(market_data[0].get("Ticker") or market_data[0].get("ticker") or "BTC")
            trades = [{"action": "STAY", "ticker": valid_ticker, "quantity": 0}]
        else:
            trades = [{"action": "STAY", "ticker": "BTC", "quantity": 0}]
    
    # Ensure every trade in the list has a string ticker
    for t in trades:
        if not isinstance(t.get("ticker"), str):
            t["ticker"] = str(t.get("ticker") or "BTC")

    # 4. Log to history
    file_exists = os.path.isfile(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["id", "recommendation"])
        writer.writerow([tick_id, json.dumps(trades)])

    # 5. POST to Mothership
    trade_payload = {"id": tick_id, "trades": trades}
    headers = {"x-api-key": Config.API_KEY, "Content-Type": "application/json"}

    try:
        response = requests.post(MOTHERSHIP_URL, json=trade_payload, headers=headers, timeout=25)
        if response.status_code == 200:
            ms_data = response.json()
            new_pos = ms_data.get("Positions") or ms_data.get("positions") or []
            with open(POSITIONS_FILE, "w") as f:
                json.dump(new_pos, f, indent=4)
            return {"result": "success", "mothership_response": ms_data}
        else:
            print(f"MOTHERSHIP ERROR: {response.text}")
            return {"result": "failure", "message": response.text}
    except Exception as e:
        return {"result": "failure", "message": str(e)}