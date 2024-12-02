"""
When processing the PDFs, if there is an interruption some PDFs might stay in the state "PROCESSING" while
not entierly processed, and will never be queued for proper processing again. So once in a while, run this 
query to reset the "PROCESSING" status.

"""
from app.repository.db import db

if __name__ == "__main__":

    var = db.reset_processing()
    while var:
        var = db.reset_processing()