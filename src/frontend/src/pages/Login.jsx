import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../services/api'
import { userService } from '../services/api'
import { useUser } from '../UserContext'
import Logo from '../components/Logo'

export default function Login() {
  const [username, setUsername] = useState('')
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')
  const { signIn } = useUser()
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      if (creating) {
        const res = await userService.create({ username })
        signIn(res.data.data)
      } else {
        signIn(await login(username))
      }
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.error || err.message)
    }
  }

  return (
    <form onSubmit={submit} className="login">
      <Logo size={120} />
      <h2>{creating ? 'Create account' : 'Sign in'}</h2>
      <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <button type="submit">{creating ? 'Sign up' : 'Log in'}</button>
      <button type="button" onClick={() => setCreating(!creating)}>
        {creating ? 'I already have an account' : 'New here? Create account'}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  )
}