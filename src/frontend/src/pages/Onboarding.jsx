import { useEffect, useState } from 'react'
import { getMovies, getGenres } from '../services/api'
import { useUser } from '../UserContext'
import MovieCard from '../components/MovieCard'

export const REQUIRED = 10
const PAGE = 24

export default function Onboarding({ count, onRated, onDone }) {
  const { user } = useUser()
  const [movies, setMovies] = useState([])
  const [genres, setGenres] = useState([])
  const [search, setSearch] = useState('')
  const [genre, setGenre] = useState('')
  const [page, setPage] = useState(0)

  useEffect(() => {
    getGenres().then((g) => setGenres(g.map((x) => x.genre))).catch(() => {})
  }, [])

  useEffect(() => { setPage(0) }, [search, genre])

  useEffect(() => {
    // the backend's title search ignores offset, so fetch a bigger batch when searching
    const limit = search ? 48 : PAGE
    getMovies({ search, genre, limit, offset: search ? 0 : page * PAGE })
      .then(setMovies)
      .catch(() => {})
  }, [search, genre, page])

  const done = count >= REQUIRED

  return (
    <div>
      <h2>Welcome, {user.username}!</h2>
      <p>
        Rate at least {REQUIRED} movies so we can learn your taste. Don't see anything you know?
        Search, pick a genre, or flip through the pages.
      </p>

      <div className="progress"><div style={{ width: `${Math.min(count / REQUIRED, 1) * 100}%` }} /></div>
      <p className="muted">{Math.min(count, REQUIRED)} / {REQUIRED} rated</p>
      {done && <button className="primary" onClick={onDone}>Continue to the app →</button>}

      <div className="toolbar">
        <input placeholder="Search movies..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <select value={genre} onChange={(e) => setGenre(e.target.value)}>
          <option value="">All genres</option>
          {genres.map((g) => <option key={g}>{g}</option>)}
        </select>
        <button onClick={() => { setSearch(''); setPage(Math.floor(Math.random() * 60)) }}>Surprise me</button>
      </div>

      <div className="grid">
        {movies.map((m) => (
          <MovieCard key={m.movie_id} movie={m} onRated={onRated} />
        ))}
      </div>

      {!search && (
        <div className="pager">
          <button disabled={page === 0} onClick={() => setPage(page - 1)}>Prev</button>
          <span>Page {page + 1}</span>
          <button disabled={movies.length < PAGE} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      )}
    </div>
  )
}