import os

# Optionally load environment variables from .env file if present
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k and k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'smart-pantry-dev-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

    # AI Configuration
    AI_API_KEY = os.environ.get('AI_API_KEY') or os.environ.get('GEMINI_API_KEY')
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'gemini')
    AI_MODEL = os.environ.get('AI_MODEL', 'gemini-2.5-flash')
