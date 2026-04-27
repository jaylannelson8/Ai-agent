import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CHATGPT_KEY = os.getenv("CHATGPT_KEY")
    API_KEY = os.getenv("API_KEY")