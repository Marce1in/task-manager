from dotenv import load_dotenv
from waitress import serve
from app import app
import os

if __name__ == '__main__':
    # Load .env
    load_dotenv()

    serve(app, port=os.environ["PRODUCTION_PORT"], host=os.environ["PRODUCTION_HOST"])
