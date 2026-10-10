from .settings import *

DEBUG = False
ALLOWED_HOSTS = ["example.ir"]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": "localhost", #db_when we dockerize it 
        "PORT": "5432",
    }
}
