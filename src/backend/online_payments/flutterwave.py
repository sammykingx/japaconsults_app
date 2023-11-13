from rave_python import Rave
from dotenv import load_dotenv
import os


load_dotenv()
rave_pay = Rave(
    os.getenv("LIVE_PUBLIC_KEY"),
    os.getenv("LIVE_SECRET_KEY"),
    production=True,
)
