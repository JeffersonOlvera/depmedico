import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    API_URL = os.getenv("API_URL")
    DEBUG = os.getenv("DEBUG", "False") == "True"

class DevelopmentConfig(Config):
    ENV = "dev"
    DEBUG = True

class ProductionConfig(Config):
    ENV = "prod"
    DEBUG = False

config_by_name = {
    "dev": DevelopmentConfig,
    "prod": ProductionConfig
}
