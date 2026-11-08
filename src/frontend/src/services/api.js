/** MovieLens frontend Axios service. Place in src/services/api.js. */
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5001/api',
  headers: { 'Content-Type': 'application/json' },
});

export const loginService = {
  login: (username) => api.post('/login', { username }),
};

export const userService = {
  getAll: (limit = 100, offset = 0) => api.get('/users', { params: { limit, offset } }),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
};

export const movieService = {
  getAll: (limit = 100, offset = 0) => api.get('/movies', { params: { limit, offset } }),
  getById: (id) => api.get(`/movies/${id}`),
  search: (title) => api.get('/movies', { params: { search: title } }),
};

export const posterService = {
  getAll: (limit = 100, offset = 0) => api.get('/posters', { params: { limit, offset } }),
  getByMovie: (movieId) => api.get(`/posters/${movieId}`),
};

export const ratingService = {
  getAll: (limit = 100, offset = 0) => api.get('/ratings', { params: { limit, offset } }),
  getByUser: (userId, limit = 100, offset = 0) => api.get(`/ratings/user/${userId}`, { params: { limit, offset } }),
  getByMovie: (movieId, limit = 100, offset = 0) => api.get(`/ratings/movie/${movieId}`, { params: { limit, offset } }),
  getByUserAndMovie: (userId, movieId) => api.get(`/ratings/${userId}/${movieId}`),
  create: (userId, movieId, rating) => api.post('/ratings', { user_id: userId, movie_id: movieId, rating }),
  update: (userId, movieId, rating) => api.put(`/ratings/${userId}/${movieId}`, { rating }),
  delete: (userId, movieId) => api.delete(`/ratings/${userId}/${movieId}`),
};

export default api;
