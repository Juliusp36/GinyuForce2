import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { UserProvider, useUser } from './UserContext'
import Login from './pages/Login'
import Home from './pages/Home'
import Recommendations from './pages/Recommendations'
import Onboarding, { REQUIRED } from './pages/Onboarding'
import Logo from './components/Logo'
import { getUserRatings } from './services/api'

function Shell() {
  const { user, signOut } = useUser()
  const [count, setCount] = useState(null)
  const [onboarding, setOnboarding] = useState(false)

  useEffect(() => {
    if (!user) {
      setCount(null)
      return
    }
    getUserRatings(user.user_id)
      .then((r) => { setCount(r.length); setOnboarding(r.length < REQUIRED) })
      .catch(() => { setCount(0); setOnboarding(true) })
  }, [user])

  // 1. Not logged in: show the sign-in page
  if (!user) {
    return (
      <Routes>
        <Route path="*" element={<Login />} />
      </Routes>
    )
  }

  // 2. Logged in, still checking how many movies they've rated
  if (count === null) return <p style={{ padding: 24 }}>Loading...</p>

  // 3. Fewer than 10 ratings: onboarding
  if (onboarding) {
    return (
      <main>
        <Onboarding
          count={count}
          onRated={() => setCount((c) => c + 1)}
          onDone={() => setOnboarding(false)}
        />
      </main>
    )
  }

  // 4. Normal app
  return (
    <>
      <nav>
        <NavLink to="/" className="brand"><Logo size={44} /></NavLink>
        <NavLink to="/" end>Browse</NavLink>
        <NavLink to="/recommendations">For You</NavLink>
        <span className="spacer" />
        <span>{user.username}</span>
        <button onClick={signOut}>Log out</button>
      </nav>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/recommendations" element={<Recommendations />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </main>
    </>
  )
}

export default function App() {
  return (
    <UserProvider>
      <BrowserRouter>
        <Shell />
      </BrowserRouter>
    </UserProvider>
  )
}