import os    
from starlette.config import Config


# get current directory 
path = os.getcwd() 

class Settings:
    _env_file = os.path.join(path, '.env')
    _config = Config(_env_file)

    # register models
    models_path = [
        'atom.user.models',
        'atom.chat.models',
        'atom.action.bookmark.models',
        'atom.action.like.models',
        'atom.action.spam.models',
        'atom.action.comment.models',
        'atom.action.block.models',
        'atom.action.rating.models',
        #admin
        'atom.option.models',
        # post
        'atom.home.post.models'
        ]

    SERVICE_NAME = _config.get("SERVICE_NAME", cast=str, default="chatbook-backend")
    SERVICE_HOST = _config.get("SERVICE_HOST", cast=str, default="0.0.0.0")
    SERVICE_PORT = _config.get("SERVICE_PORT", cast=int, default=8080)
    SERVICE_ENV = _config.get("SERVICE_ENV", cast=str, default="local")
    DEBUG = _config.get("DEBUG", cast=bool, default=True)
    SECRET_KEY = _config.get("SECRET_KEY", cast=str, default="Asjfwol2asfs13tg123142Ags1k23hnSA36as6f4qQ324FEsvb")
    ALLOWED_HOSTS = _config.get("ALLOWED_HOSTS", cast=str, default='*')
    LOG_LEVEL = _config.get("LOG_LEVEL", cast=str, default='debug')

    DB_HOST = _config.get("DB_HOST", cast=str, default='127.0.0.1')
    DB_PORT = _config.get("DB_PORT", cast=int, default=5432)
    DB_NAME = _config.get("DB_NAME", cast=str, default='chatbook_test')
    DB_USER = _config.get("DB_USER", cast=str, default='postgres')
    DB_PASS = _config.get("DB_PASS", cast=str, default='123456')
    DB_MAX_CONN = _config.get("DB_MAX_CONN", cast=int, default=100)
    DB_MIN_CONN = _config.get("DB_MIN_CONN", cast=int, default=1)

    MSG91_AUTHKEY = _config.get("MSG91_AUTHKEY", cast=str, default="182905AumgOuUUeat5a03f289")
    MST91_OTP_TEMPLATE_ID = _config.get("MST91_OTP_TEMPLATE_ID", cast=str, default="5e2c0aa652a1b10bb76ca303")

    OTP_VALIDITY_PERIOD = _config.get("OTP_VALIDITY_PERIOD", cast=int, default=10000)
    OTP_LENGTH = _config.get("OTP_LENGTH", cast=int, default=4)

    TOKEN_VALIDITY_PERIOD = _config.get("TOKEN_VALIDITY_PERIOD", cast=int, default=60 * 60 * 24 * 200)
    
    def get_db_url(self):
        db_config = {
            'user': self.DB_USER,
            'pass': self.DB_PASS,
            'host': self.DB_HOST,
            'port': self.DB_PORT,
            'name': self.DB_NAME,
            'maxsize': self.DB_MAX_CONN,
            'minsize': self.DB_MIN_CONN
        }
        return 'postgres://{user}:{pass}@{host}:{port}/{name}?maxsize={maxsize}&minsize={minsize}'.format(**db_config)


settings = Settings()

