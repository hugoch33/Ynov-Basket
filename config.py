import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
