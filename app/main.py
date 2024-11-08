from app.repository.db import db


if __name__ == '__main__':
    db.create_user(name="Alice", email="alice@example.com")
    user = db.get_user(name="Alice")
    
    print(user)
    print()