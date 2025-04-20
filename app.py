from flask import Flask, jsonify, request
from pymongo import MongoClient, errors
from bson import ObjectId
from bson.errors import InvalidId

app = Flask(__name__)

try:
    client = MongoClient("mongodb://admin:admin@mongodb-service:27017/", serverSelectionTimeoutMS=5000)
    db = client['bookstore']

    client.server_info()
    print("Connected to MongoDB.")
except errors.ServerSelectionTimeoutError as e:
    print(f"Failed to connect to MongoDB: {e}")
    db = None


def invalid_json_payload():
    return jsonify({'error': 'Invalid JSON payload'}), 400

def invalid_object_id():
    return jsonify({'error': 'Invalid book ID format'}), 400

def not_found(message='Resource not found'):
    return jsonify({'error': message}), 404

def mongo_error(e):
    return jsonify({'error': f'MongoDB error: {str(e)}'}), 500



@app.route('/books', methods=['POST'])
def create_book():
    if not request.json:
        return invalid_json_payload()
    try:
        book = request.json
        result = db.books.insert_one(book)
        return jsonify({'_id': str(result.inserted_id)}), 201
    except errors.PyMongoError as e:
        return mongo_error(e)



@app.route('/books', methods=['GET'])
def get_books():
    try:
        books = list(db.books.find())
        for book in books:
            book['_id'] = str(book['_id'])
        return jsonify(books), 200
    except errors.PyMongoError as e:
        return mongo_error(e)



@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    if not request.json:
        return invalid_json_payload()
    try:

        try:
            object_id = ObjectId(book_id)
        except InvalidId:
            return invalid_object_id()

        updated_book = request.json
        result = db.books.update_one({'_id': object_id}, {'$set': updated_book})

        if result.matched_count == 0:
            return not_found('Book not found')

        return jsonify({'message': 'Book updated'}), 200
    except errors.PyMongoError as e:
        return mongo_error(e)



@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    try:

        try:
            object_id = ObjectId(book_id)
        except InvalidId:
            return invalid_object_id()

        result = db.books.delete_one({'_id': object_id})

        if result.deleted_count == 0:
            return not_found('Book not found')

        return jsonify({'message': 'Book deleted'}), 200
    except errors.PyMongoError as e:
        return mongo_error(e)


if __name__ == '__main__':
    if db:
        app.run(host='0.0.0.0', debug=True)
    else:
        print("Application cannot start as the database connection failed.")