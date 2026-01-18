from flask import Flask
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_USER = os.environ.get('MONGO_USER', 'root')
MONGO_PASS = os.environ.get('MONGO_PASS', 'password')

client = MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:27017/")
db = client.flask_db
todos = db.todos

@app.route('/')
def home():
    todos.insert_one({'task': 'Visit Page'})
    count = todos.count_documents({})
    return f"<h1>Hello! This page has been visited {count} times.</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
