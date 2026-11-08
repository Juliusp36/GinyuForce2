"""MovieLens classroom demo REST API (Flask + SQLite)."""
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
from db_config import DB_PATH
from user import User
from movie import Movie
from rating import Rating
from movie_poster import MoviePoster

app = Flask(__name__)
CORS(app, resources={r'/api/*': {'origins': ['http://localhost:3000', 'http://localhost:5173']}})


def respond(data, status=200):
    return jsonify({'data': data}), status


def body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError('JSON object body required')
    return data


def paging():
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    if not 1 <= limit <= 500 or offset < 0:
        raise ValueError('limit must be 1–500 and offset must be nonnegative')
    return limit, offset


def fields(data, allowed):
    unknown = set(data) - set(allowed)
    if unknown:
        raise ValueError('Unsupported fields: ' + ', '.join(sorted(unknown)))
    return {key: value for key, value in data.items() if key in allowed}


@app.errorhandler(ValueError)
def invalid(error):
    return jsonify({'error': str(error)}), 400


@app.errorhandler(sqlite3.IntegrityError)
def conflict(error):
    return jsonify({'error': 'Database constraint violation'}), 409


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.get('/api/health')
def health():
    return respond({'status': 'ok', 'database_exists': DB_PATH.exists()})


@app.post('/api/login')
def login():
    """Demo-only username lookup. This is NOT secure authentication."""
    username = body().get('username')
    if not isinstance(username, str) or not username.strip():
        raise ValueError('username is required')
    user = User.get_by_username(username.strip())
    if not user:
        return jsonify({'error': 'Username not found'}), 404
    return respond(user)


@app.get('/api/users')
def users():
    return respond(User.get_all(*paging()))


@app.get('/api/users/<int:user_id>')
def user_by_id(user_id):
    user = User.get_by_id(user_id)
    return respond(user) if user else (jsonify({'error': 'User not found'}), 404)


@app.post('/api/users')
def create_user():
    data = fields(body(), ['username', 'age', 'gender', 'occupation', 'zip_code'])
    username = data.get('username')
    if not isinstance(username, str) or not username.strip():
        raise ValueError('username is required')
    data['username'] = username.strip()
    if User.get_by_username(data['username']):
        return jsonify({'error': 'Username already exists'}), 409
    user_id = User.create(**data)
    return respond(User.get_by_id(user_id), 201)


@app.put('/api/users/<int:user_id>')
def update_user(user_id):
    if not User.get_by_id(user_id):
        return jsonify({'error': 'User not found'}), 404
    data = fields(body(), ['username', 'age', 'gender', 'occupation', 'zip_code'])
    if not data:
        raise ValueError('At least one field is required')
    if 'username' in data and User.get_by_username(data['username']):
        existing = User.get_by_username(data['username'])
        if existing['user_id'] != user_id:
            return jsonify({'error': 'Username already exists'}), 409
    User.update(user_id, **data)
    return respond(User.get_by_id(user_id))


@app.delete('/api/users/<int:user_id>')
def delete_user(user_id):
    if not User.delete(user_id):
        return jsonify({'error': 'User not found'}), 404
    return '', 204


@app.get('/api/movies')
def movies():
    limit, offset = paging()
    title = request.args.get('search', '').strip()
    if title:
        return respond(Movie.search(title, limit))
    return respond(Movie.get_all(limit, offset))


@app.get('/api/movies/<int:movie_id>')
def movie_by_id(movie_id):
    movie = Movie.get_by_id(movie_id)
    return respond(movie) if movie else (jsonify({'error': 'Movie not found'}), 404)


@app.get('/api/posters')
def posters():
    return respond(MoviePoster.get_all(*paging()))


@app.get('/api/posters/<int:movie_id>')
def poster_by_movie(movie_id):
    poster = MoviePoster.get_by_movie(movie_id)
    return respond(poster) if poster else (jsonify({'error': 'Poster not found'}), 404)


@app.get('/api/ratings')
def ratings():
    return respond(Rating.get_all(*paging()))


@app.get('/api/ratings/user/<int:user_id>')
def ratings_by_user(user_id):
    if not User.get_by_id(user_id):
        return jsonify({'error': 'User not found'}), 404
    return respond(Rating.get_by_user(user_id, *paging()))


@app.get('/api/ratings/movie/<int:movie_id>')
def ratings_by_movie(movie_id):
    if not Movie.get_by_id(movie_id):
        return jsonify({'error': 'Movie not found'}), 404
    return respond(Rating.get_by_movie(movie_id, *paging()))


@app.get('/api/ratings/<int:user_id>/<int:movie_id>')
def rating_by_pair(user_id, movie_id):
    rating = Rating.get_by_user_and_movie(user_id, movie_id)
    return respond(rating) if rating else (jsonify({'error': 'Rating not found'}), 404)


def validated_rating(value):
    if type(value) is not int or not 1 <= value <= 5:
        raise ValueError('rating must be an integer between 1 and 5')
    return value


@app.post('/api/ratings')
def create_rating():
    data = fields(body(), ['user_id', 'movie_id', 'rating'])
    if type(data.get('user_id')) is not int or type(data.get('movie_id')) is not int:
        raise ValueError('user_id and movie_id must be integers')
    rating = validated_rating(data.get('rating'))
    user_id, movie_id = data['user_id'], data['movie_id']
    if not User.get_by_id(user_id) or not Movie.get_by_id(movie_id):
        return jsonify({'error': 'User or movie not found'}), 404
    if Rating.get_by_user_and_movie(user_id, movie_id):
        return jsonify({'error': 'Rating already exists; use PUT to update'}), 409
    Rating.create(user_id, movie_id, rating)
    return respond(Rating.get_by_user_and_movie(user_id, movie_id), 201)


@app.put('/api/ratings/<int:user_id>/<int:movie_id>')
def update_rating(user_id, movie_id):
    data = fields(body(), ['rating'])
    rating = validated_rating(data.get('rating'))
    if not Rating.update(user_id, movie_id, rating):
        return jsonify({'error': 'Rating not found'}), 404
    return respond(Rating.get_by_user_and_movie(user_id, movie_id))


@app.delete('/api/ratings/<int:user_id>/<int:movie_id>')
def delete_rating(user_id, movie_id):
    if not Rating.delete(user_id, movie_id):
        return jsonify({'error': 'Rating not found'}), 404
    return '', 204


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)
