import { useEffect, useState } from 'react'
import { getMovies, getGenres, getUserRatings } from '../services/api'
import { useUser } from '../UserContext'
import MovieCard from '../components/MovieCard'

const PAGE = 24

export default function Home() {
  const { user } = useUser()
  const [movies, setMovies] = useState([])
  const [genres, setGenres] = useState([])
  const [myRatings, setMyRatings] = useState({})
  const [search, setSearch] = useState('')
  const [genre, setGenre] = useState('')
  const [page, setPage] = useState(0)
  const [error, setError] = useState('')

  useEffect(() => {
    getGenres().then((g) => setGenres(g.map((x) => x.genre))).catch(() => {})
    getUserRatings(user.user_id)
      .then((rs) => setMyRatings(Object.fromEntries(rs.map((r) => [r.movie_id, r.rating]))))
      .catch(() => {})
  }, [user.user_id])

  useEffect(() => { setPage(0) }, [search, genre])

  useEffect(() => {
    getMovies({ search, genre, limit: PAGE, offset: page * PAGE })
      .then(setMovies)
      .catch((e) => setError(e.message))
  }, [search, genre, page])

  return (
    <div>
      <div className="toolbar">
        <input placeholder="Search movies..." value={search} onChange={(e) => setSearch(e.target.value)} />
        <select value={genre} onChange={(e) => setGenre(e.target.value)}>
          <option value="">All genres</option>
          {genres.map((g) => <option key={g}>{g}</option>)}
        </select>
      </div>
      {error && <p className="error">{error}</p>}
      <div className="grid">
        {movies.map((m) => (
          <MovieCard key={m.movie_id} movie={m} initialRating={myRatings[m.movie_id] || 0} />
        ))}
      </div>
      <div className="pager">
        <button disabled={page === 0} onClick={() => setPage(page - 1)}>Prev</button>
        <span>Page {page + 1}</span>
        <button disabled={movies.length < PAGE} onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  )
}