from app.repository.db import db

if __name__ == "__main__":

    var = db.reset_hash()
    while var:
        var = db.reset_hash()