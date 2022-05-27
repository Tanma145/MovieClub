import hikari
import os
from dotenv import load_dotenv


def init():
    try:
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            # keys
            API_KEY = os.environ.get("API_KEY")
            DATABASE_URL = os.environ.get("DATABASE_URL")
            OOF = os.environ.get("OOF")
            if None in (API_KEY, DATABASE_URL, OOF):
                raise Exception
    except Exception as e:
        print("Some tokens are missing")
        os.close(1)


if __name__ == '__main__':
    init()
    print('hello!')
