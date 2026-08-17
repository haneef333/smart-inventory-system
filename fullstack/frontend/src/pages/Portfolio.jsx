import { useEffect, useRef, useState } from 'react'
import { getPortfolioItems, addPortfolioItem, deletePortfolioItem, portfolioImageUrl } from '../api/client'
import Panel from '../components/Panel'
import { input, label, field, buttonPrimary, buttonDanger } from '../components/ui'

export default function Portfolio() {
  const [items, setItems] = useState([])
  const [title, setTitle] = useState('')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const fileInputRef = useRef(null)

  const load = () => {
    getPortfolioItems().then(setItems)
  }

  useEffect(() => { load() }, [])

  function handleFileChange(e) {
    const f = e.target.files?.[0]
    setFile(f || null)
    setPreview(f ? URL.createObjectURL(f) : null)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    if (!title.trim()) { setError('Give this photo a title.'); return }
    if (!file) { setError('Choose a photo to upload.'); return }

    setSubmitting(true)
    try {
      await addPortfolioItem(title.trim(), file)
      setTitle('')
      setFile(null)
      setPreview(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
      load()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Upload failed.')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id) {
    await deletePortfolioItem(id)
    load()
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 30 }}>Portfolio</h1>
        <p style={{ color: 'var(--flour-dim)', marginTop: 6 }}>Show off your bakes</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 20, alignItems: 'start' }}>
        <Panel title="Add a photo">
          <form onSubmit={handleSubmit}>
            <div style={field}>
              <label style={label}>Title</label>
              <input
                type="text" style={input} placeholder="e.g. Rainbow drip cake"
                value={title} onChange={e => setTitle(e.target.value)}
              />
            </div>
            <div style={field}>
              <label style={label}>Photo</label>
              <input
                ref={fileInputRef} type="file" accept="image/*" style={input}
                onChange={handleFileChange}
              />
            </div>

            {preview && (
              <div style={{ marginBottom: 14 }}>
                <img src={preview} alt="Preview" style={{ width: '100%', borderRadius: 10, display: 'block' }} />
              </div>
            )}

            <button type="submit" disabled={submitting} style={{ ...buttonPrimary, width: '100%' }}>
              {submitting ? 'Uploading…' : '+ Add to portfolio'}
            </button>
          </form>

          {error && (
            <div style={{ marginTop: 14, padding: 12, borderRadius: 8, background: 'rgba(193,80,58,0.1)', border: '1px solid rgba(193,80,58,0.35)' }}>
              <div style={{ color: 'var(--jam)', fontSize: 12 }}>{error}</div>
            </div>
          )}
        </Panel>

        <Panel title={`Your bakes (${items.length})`}>
          {items.length === 0 && (
            <div style={{ color: 'var(--flour-dim)', fontSize: 13 }}>
              No photos yet — add your first bake to start your portfolio.
            </div>
          )}

          <div style={grid}>
            {items.map(item => (
              <div key={item.id} style={card}>
                <img
                  src={portfolioImageUrl(item.image_filename)}
                  alt={item.title}
                  style={{ width: '100%', aspectRatio: '1', objectFit: 'cover', display: 'block' }}
                />
                <div style={{ padding: '10px 12px' }}>
                  <div style={{ fontSize: 13, marginBottom: 8 }}>{item.title}</div>
                  <button style={buttonDanger} onClick={() => handleDelete(item.id)}>Delete</button>
                </div>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  )
}

const grid = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
  gap: 14,
}

const card = {
  background: 'var(--charcoal-soft)',
  border: '1px solid var(--panel-border)',
  borderRadius: 10,
  overflow: 'hidden',
}
