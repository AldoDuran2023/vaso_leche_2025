from app import app  
from src.database.db import db
from dotenv import load_dotenv

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True)