import os

from dotenv import load_dotenv

load_dotenv()
DJANGO_SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
SITE_URL = os.environ.get("SITE_URL")

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")

AUTH_EMAIL_FROM = os.environ.get("AUTH_EMAIL_FROM")
AUTH_EMAIL_BCC = os.environ.get("AUTH_EMAIL_BCC")

AUTH_EMAIL_HOST = os.environ.get("AUTH_EMAIL_HOST")
AUTH_EMAIL_PORT = os.environ.get("AUTH_EMAIL_PORT")
AUTH_EMAIL_HOST_USER = os.environ.get("AUTH_EMAIL_HOST_USER")
AUTH_EMAIL_HOST_PASSWORD = os.environ.get("AUTH_EMAIL_HOST_PASSWORD")
