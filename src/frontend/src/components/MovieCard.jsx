import { useEffect, useState } from 'react'
import { getPoster, rateMovie } from '../services/api'
import { useUser } from '../UserContext'
import StarRating from './StarRating'

export default function MovieCard({ movie, initialRating = 0, posterUrl, predicted, onRated }) {
  const { user } = useUser()
  const [poster, setPoster] = useState(posterUrl || null)
  const [rating, setRating] = useState(initialRating)

  useEffect(() => {
    if (posterUrl) return
    getPoster(movie.movie_id).then((p) => p && setPoster(p.poster_url))
  }, [movie.movie_id, posterUrl])

  const handleRate = async (n) => {
    const previous = rating
    setRating(n)
    try {
      await rateMovie(user.user_id, movie.movie_id, n)
      if (previous === 0 && onRated) onRated()
    } catch {
      setRating(previous)
      alert('Could not save rating')
    }
  }

  return (
    <div className="card">
      {poster ? <img src={poster} alt={movie.title} /> : <div className="no-poster">No poster</div>}
      <p className="title">{movie.title}</p>
      {predicted != null && <p className="muted">Predicted: {predicted.toFixed(2)} ★</p>}
      <StarRating value={rating} onRate={handleRate} />
    </div>
  )
}