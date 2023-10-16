from rave_python import Rave
from dotnv import load_dotenv
import os


load_dotenv()
rave_pay = Rave(os.getenv, os.getenv, production=True)
