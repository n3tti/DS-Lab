import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.dirname(os.path.dirname(BASE_DIR)) + "/data/"

PARENTS_DIR = DATA_DIR + "parents.json"
METADATA_DIR = DATA_DIR + "metadata.json"

TEXT_DIR = DATA_DIR + "text/html/"
IMAGE_DIR = DATA_DIR + "image/png/"
APPLICATION_DIR = DATA_DIR + "application/pdf/"
