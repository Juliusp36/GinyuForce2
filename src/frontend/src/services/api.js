/** MovieLens frontend Axios service. Place in src/services/api.js. */
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5001/api',
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
  query: ({ search, genre, limit = 24, offset = 0 } = {}) =>
    api.get('/movies', {
      params: { limit, offset, ...(search && { search }), ...(genre && { genre }) },
    }),
};

export const genreService = {
  getAll: () => api.get('/genres'),
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

export const recommendationService = {
  getForUser: (userId, { genre, limit = 24, offset = 0 } = {}) =>
    api.get(`/users/${userId}/recommendations`, {
      params: { limit, offset, ...(genre && { genre }) },
    }),
};

export default api;

/* ---------- Convenience wrappers used by the React pages ---------- */

async function call(promise) {
  try {
    const res = await promise;
    return res.data?.data ?? null;
  } catch (err) {
    const e = new Error(err.response?.data?.error || err.message);
    e.status = err.response?.status;
    throw e;
  }
}

export const login = (username) => call(loginService.login(username));
export const getMovies = (opts) => call(movieService.query(opts));
export const getGenres = () => call(genreService.getAll());
export const getUserRatings = (userId) => call(ratingService.getByUser(userId, 500, 0));
export const getRecommendations = (userId, opts) => call(recommendationService.getForUser(userId, opts));

const posterCache = {};
export const getPoster = (movieId) => {
  if (!(movieId in posterCache)) {
    posterCache[movieId] = call(posterService.getByMovie(movieId)).catch(() => null);
  }
  return posterCache[movieId];
};

export async function rateMovie(userId, movieId, rating) {
  try {
    return await call(ratingService.create(userId, movieId, rating));
  } catch (e) {
    if (e.status === 409) return call(ratingService.update(userId, movieId, rating));
    throw e;
  }
}