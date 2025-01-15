import os
from dotenv import load_dotenv

load_dotenv() 

API_TOKEN = os.getenv("API_TOKEN")

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")

TAX_INFO_IMG_URL = os.getenv("TAX_INFO_IMG_URL")
START_VIDEO_URL = os.getenv("START_VIDEO_URL")

PORT = os.getenv("PORT")