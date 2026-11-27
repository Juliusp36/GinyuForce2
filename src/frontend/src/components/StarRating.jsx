import { useState } from 'react'

export default function StarRating({ value = 0, onRate }) {
  const [hover, setHover] = useState(0)
  return (
    <div>
      {[1, 2, 3, 4, 5].map((n) => (
        <span
          key={n}
          style={{ cursor: 'pointer', fontSize: 22, color: n <= (hover || value) ? '#f5b301' : '#888' }}
          onMouseEnter={() => setHover(n)}
          onMouseLeave={() => setHover(0)}
          onClick={() => onRate(n)}
        >
          ★
        </span>
      ))}
    </div>
  )
}