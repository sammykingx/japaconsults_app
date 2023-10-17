from rave_python import Rave
from dotenv import load_dotenv
import os


load_dotenv()
rave_pay = Rave(os.getenv("RAVE_PUBLIC_KEY"), os.getenv("RAVE_SECRET_KEY"), production=True)
