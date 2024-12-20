import logging
import os

from dotenv import load_dotenv

# All environmental variables should be defined in the .env

load_dotenv(override=True)


DEBUG = os.getenv("DEBUG", "").lower() != "false"

LOG_LEVEL = getattr(logging, os.getenv("LOG_LEVEL", "NOTSET").upper())

NEW_RELIC_LICENSE_KEY = os.getenv("NEW_RELIC_LICENSE_KEY")


DATABASE_URL = os.environ["DATABASE_URL"]

# The SAVE_DOWNLOADED_FILE variable might not be needed
SAVE_DOWNLOADED_FILE = "/capstor/store/cscs/swissai/a06/users/group_06/test/DLFiles/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.dirname(BASE_DIR) + "/data/"

PERSISTENCE_BASE = os.path.dirname(BASE_DIR) + "/.persistence/"
JOBDIR = PERSISTENCE_BASE + "jobdir/"
