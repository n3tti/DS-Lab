import os
from dotenv import load_dotenv


load_dotenv(override=True)

LOG_LEVEL_DISABLE = os.getenv("LOG_LEVEL", "DEBUG")  # This level and lower


# NEW_RELIC_LICENSE_KEY = os.getenv("NEW_RELIC_LICENSE_KEY")


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/example.db")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.dirname(BASE_DIR) + "/data/"

# PARENTS_DIR = DATA_DIR + "parents.json"
# METADATA_DIR = DATA_DIR + "metadata.json"
# PDF_FILE = DATA_DIR + "pdf.json"
# IMAGE_FILE = DATA_DIR + "image.json"

# TEXT_DIR = DATA_DIR + "text/html/"
# IMAGE_DIR = DATA_DIR + "image/png/"
# APPLICATION_DIR = DATA_DIR + "application/pdf/"

PERSISTENCE_BASE = os.path.dirname(BASE_DIR) + "/persistence/"
JOBDIR = PERSISTENCE_BASE + "jobdir/"
# SAVE_IDS_FILE = PERSISTENCE_BASE + "pipelines_states/seen_ids.json"
# SAVE_LAST_ID_FILE = PERSISTENCE_BASE + "pipelines_states/last_id.json"
