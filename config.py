import os

try:
    from config_secrets import Secrets
except ImportError:
    class Secrets(object):
        SECRET_KEY = None
        CLIENT_ID = None
        CLIENT_SECRET = None
        AUTHORIZATION = None


uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

class Config(object):
    SQLALCHEMY_DATABASE_URI = uri if uri else "postgresql:///sound-explorer"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SCOPE = "playlist-modify-private playlist-modify-public playlist-read-collaborative"
    REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/callback/")
    SECRET_KEY = os.getenv("SECRET_KEY", Secrets.SECRET_KEY)
    CLIENT_ID = os.getenv("CLIENT_ID", Secrets.CLIENT_ID)
    CLIENT_SECRET = os.getenv("CLIENT_SECRET", Secrets.CLIENT_SECRET)
    AUTHORIZATION = os.getenv("AUTHORIZATION", Secrets.AUTHORIZATION)
