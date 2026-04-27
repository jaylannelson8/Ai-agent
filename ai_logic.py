import os
import json
from openai import OpenAI
from config import Config

client = OpenAI(api_key=Config.CHATGPT_KEY)

def get_trading_recommendation(market_data):
    # Model set to gpt-5-nano as requested
    prompt = f"""
    Analyze: {market_data}. 
    MANDATORY: Return a JSON object with a "trades" key. 
    Suggest trades ONLY for tickers found in the market_data provided.
    The "trades" list MUST NOT BE EMPTY.
    Format: {{ "trades": [{{ "action": "BUY/SELL/STAY", "ticker": "string", "quantity": int }}] }}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano", 
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=10
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Logic Error (gpt-5-nano): {e}")
        return json.dumps({"trades": []})