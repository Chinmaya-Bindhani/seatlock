from . base import  *


from pathlib import Path
import environ

PROJECT_ROOT = Path(__file__).resolve().parents[2]
environ.Env.read_env(PROJECT_ROOT / ".env")



#OVERRIDING THE DATABASE CONFIGURATIONS FROM BASE.PY FOR LOCAL DEVELOPMENT
from os import getenv

DATABASES = {
    "default": {
        "ENGINE": f"django.db.backends.{getenv('WHICH_DB')}",
        "NAME": getenv("DB_NAME"),
        "USER": getenv("DB_USER"),
        "PASSWORD": getenv("DB_PASSWORD"),
    }
}

