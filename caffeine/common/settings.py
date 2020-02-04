from environs import Env

from caffeine.common.datastructure.security import Secret


class Settings:
    DEBUG = True
    SECRET_KEY = None
    SENTRY_URL = ""
    DB_DSN = ""

    JWT_SECRET = None
    JWT_TOKEN_EXPIRE = 600
    JWT_TOKEN_REFRESH_EXPIRE = 36000
    JWT_COOKIE_EXPIRE = 2592000
    JWT_COOKIE_KEY = "Authorization"
    JWT_COOKIE_REFRESH_KEY = "RefreshToken"

    RECAPTCHA_SECRET = None
    TEMPLATE_PATH = None

    MAIL_SERVER = ""
    MAIL_USERNAME = ""
    MAIL_PASSWORD = None
    MAIL_PORT = 993
    MAIL_USESTARTTLS = True

    ACTIVATION_LINK_TEMPLATE = ""
    RESET_PASSWORD_LINK_TEMPLATE = ""  # noqa

    CASBIN_POLICY = None
    CASBIN_MODEL = None

    def __init__(self):
        self.env = Env()

    def read_env(self):
        env = self.env
        env.read_env()
        self.DEBUG = env.bool("DEBUG", True)
        self.SECRET_KEY = Secret(env("SECRET_KEY"))
        self.SENTRY_URL = env("SENTRY_URL")
        self.DB_DSN = Secret(env("DB_DSN"))

        self.JWT_SECRET = Secret(env("JWT_SECRET"))
        self.JWT_TOKEN_EXPIRE = env.int("JWT_TOKEN_EXPIRE")
        self.JWT_TOKEN_REFRESH_EXPIRE = env.int("JWT_TOKEN_REFRESH_EXPIRE")
        self.JWT_COOKIE_EXPIRE = env.int("JWT_COOKIE_EXPIRE", 2592000)
        self.JWT_COOKIE_KEY = env("JWT_COOKIE_KEY", "Authorization")
        self.JWT_COOKIE_REFRESH_KEY = env("JWT_COOKIE_REFRESH_KEY", "RefreshToken")

        self.CASBIN_MODEL = env("CASBIN_MODEL")
        self.CASBIN_POLICY = env("CASBIN_POLICY")

        self.RECAPTCHA_SECRET = env("RECAPTCHA_SECRET")
        self.TEMPLATE_PATH = env("TEMPLATE_PATH")

        self.MAIL_SERVER = env("MAIL_SERVER")
        self.MAIL_USERNAME = env("MAIL_USERNAME")
        self.MAIL_PASSWORD = Secret(env("MAIL_PASSWORD"))
        self.MAIL_PORT = env.int("MAIL_PORT", 993)
        self.MAIL_USESTARTTLS = env.bool("MAIL_USESTARTTLS", True)
        self.ACTIVATION_LINK_TEMPLATE = env.str("ACTIVATION_LINK_TEMPLATE")
        self.RESET_PASSWORD_LINK_TEMPLATE = env.str("RESET_PASSWORD_LINK_TEMPLATE")
