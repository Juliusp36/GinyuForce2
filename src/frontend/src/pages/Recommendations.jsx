import { useEffect, useState } from 'react'
import { getRecommendations, getGenres } from '../services/api'
import { useUser } from '../UserContext'
import MovieCard from '../components/MovieCard'

const PAGE = 24

export default function Recommendations() {
  const { user } = useUser()
  const [recs, setRecs] = useState([])
  const [genres, setGenres] = useState([])
  const [genre, setGenre] = useState('')
  const [page, setPage] = useState(0)
  const [error, setError] = useState('')

  useEffect(() => {
    getGenres().then((g) => setGenres(g.map((x) => x.genre))).catch(() => {})
  }, [])

  useEffect(() => { setPage(0) }, [genre])

  useEffect(() => {
    getRecommendations(user.user_id, { genre, limit: PAGE, offset: page * PAGE })
      .then(setRecs)
      .catch((e) => setError(e.message))
  }, [user.user_id, genre, page])

  return (
    <div>
      <h2>Recommended for {user.username}</h2>
      <select value={genre} onChange={(e) => setGenre(e.target.value)}>
        <option value="">All genres</option>
        {genres.map((g) => <option key={g}>{g}</option>)}
      </select>
      {error && <p className="error">{error}</p>}
      {recs.length === 0 && !error && (
        <p className="muted" style={{ marginTop: 16 }}>
          No recommendations yet. Your ratings need to be added to the model first.
        </p>
      )}
      <div className="grid">
        {recs.map((r) => (
          <MovieCard key={r.movie_id} movie={r} posterUrl={r.poster_url} predicted={r.predicted_rating} />
        ))}
      </div>
      <div className="pager">
        <button disabled={page === 0} onClick={() => setPage(page - 1)}>Prev</button>
        <span>Page {page + 1}</span>
        <button disabled={recs.length < PAGE} onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  )
}