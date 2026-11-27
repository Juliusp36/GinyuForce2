import { createContext, useContext, useState } from 'react'

const UserContext = createContext(null)
export const useUser = () => useContext(UserContext)

export function UserProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('user')
    return saved ? JSON.parse(saved) : null
  })

  const signIn = (u) => { localStorage.setItem('user', JSON.stringify(u)); setUser(u) }
  const signOut = () => { localStorage.removeItem('user'); setUser(null) }

  return <UserContext.Provider value={{ user, signIn, signOut }}>{children}</UserContext.Provider>
}