import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

GRAPH_VERSION = os.getenv("GRAPH_VERSION")

IG_ACCOUNT_ID = os.getenv("IG_ACCOUNT_ID")
FB_PAGE_ID = os.getenv("FB_PAGE_ID")

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")