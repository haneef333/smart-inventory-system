import { useState } from 'react'
import { ownerLogin, ownerToken } from '../api/client'
import { buttonPrimary, input } from './ui'

export default function OwnerLogin({ onLoggedIn }) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      const { token } = await ownerLogin(password)
      ownerToken.set(token)
      onLoggedIn()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Could not reach the server. Try again in a moment.')
      setBusy(false)
    }
  }

  return (
    <div style={wrap}>
      <form onSubmit={submit} style={card}>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: 26, marginBottom: 6 }}>Crumb &amp; Ledger</div>
        <p style={{ color: 'var(--flour-dim)', marginBottom: 20, fontSize: 14 }}>Enter the owner password to manage stock and orders.</p>
        <label htmlFor="owner-password" style={{ display: 'block', fontSize: 13, color: 'var(--flour-dim)', marginBottom: 6 }}>Password</label>
        <input
          id="owner-password"
          type="password"
          autoComplete="current-password"
          autoFocus
          value={password}
          onChange={e => setPassword(e.target.value)}
          style={input}
          required
        />
        {error && <p style={{ color: 'var(--jam)', fontSize: 13, marginTop: 10 }}>{error}</p>}
        <button type="submit" disabled={busy} style={{ ...buttonPrimary, width: '100%', marginTop: 16, opacity: busy ? 0.6 : 1 }}>
          {busy ? 'Logging in…' : 'Log in'}
        </button>
      </form>
    </div>
  )
}

const wrap = { minHeight: '100vh', display: 'grid', placeItems: 'center', padding: 20 }
const card = {
  width: '100%', maxWidth: 380, padding: 28, borderRadius: 16,
  background: 'var(--panel)', border: '1px solid var(--panel-border)',
}
