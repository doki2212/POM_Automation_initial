# config.py
#loading up the site as well as the credentials
import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    BASE_URL = os.getenv("BASE_URL")
    if not BASE_URL:
        raise ValueError("Base URL is required, do set it up in the .env file")

    USERNAME = os.getenv("LOGIN_USERNAME","")
    PASSWORD = os.getenv("LOGIN_PASSWORD","")
    if not USERNAME or not PASSWORD:
        raise ValueError("Both Username and Password required to be in the .env file")

    DEFAULT_TAB = os.getenv("DEFAULT_TAB", "")
    DEFAULT_TAB_XPATH = os.getenv("DEFAULT_TAB_XPATH", "")  

    IMPLICIT_WAIT = 0
    EXPLICIT_WAIT = 20
