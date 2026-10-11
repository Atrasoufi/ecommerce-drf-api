from pathlib import Path
from dotenv import load_dotenv
import os

from .settings import *


BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_USER_MODEL = "accounts.UserModel"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"