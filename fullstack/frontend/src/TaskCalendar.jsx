import { useEffect, useState } from 'react'
import { getTasksForMonth, addTask, updateTask, deleteTask } from '../api/client'
import Panel from './Panel'
import { input, buttonPrimary, buttonGhost, buttonDanger } from './ui'

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function pad(n) { return String(n).padStart(2, '0') }
function toISODate(d) { return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` }
function toMonthKey(d) { return `${d.getFullYear()}-${pad(d.getMonth() + 1)}` }

export default function TaskCalendar() {
  const today = new Date()
  const [cursor, setCursor] = useState(new Date(today.getFullYear(), today.getMonth(), 1))
  const [selectedDate, setSelectedDate] = useState(toISODate(today))
  const [tasks, setTasks] = useState([])
  const [newTitle, setNewTitle] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const monthKey = toMonthKey(cursor)

  const load = () => {
    getTasksForMonth(monthKey).then(setTasks)
  }

  useEffect(() => { load() }, [monthKey])

  const daysWithTasks = new Set(tasks.filter(t => !t.is_done).map(t => t.task_date))
  const tasksForSelected = tasks.filter(t => t.task_date === selectedDate)

  function changeMonth(delta) {
    const next = new Date(cursor.getFullYear(), cursor.getMonth() + delta, 1)
    setCursor(next)
  }

  async function handleAddTask(e) {
    e.preventDefault()
    if (!newTitle.trim()) return
    setSubmitting(true)
    try {
      await addTask({ task_date: selectedDate, title: newTitle.trim() })
      setNewTitle('')
      load()
    } finally {
      setSubmitting(false)
    }
  }

  async function toggleDone(task) {
    await updateTask(task.id, { is_done: !task.is_done })
    load()
  }

  async function removeTask(id) {
    await deleteTask(id)
    load()
  }

  // Build calendar grid cells
  const firstOfMonth = new Date(cursor.getFullYear(), cursor.getMonth(), 1)
  const startWeekday = firstOfMonth.getDay()
  const daysInMonth = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 0).getDate()
  const cells = []
  for (let i = 0; i < startWeekday; i++) cells.push(null)
  for (let d = 1; d <= daysInMonth; d++) cells.push(d)

  const monthLabel = cursor.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  const selectedLabel = new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-US', {
    weekday: 'long', month: 'long', day: 'numeric', year: 'numeric',
  })

  return (
    <Panel
      title="Task calendar"
      action={
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button style={navBtn} onClick={() => changeMonth(-1)}>‹</button>
          <span style={{ fontSize: 13, minWidth: 130, textAlign: 'center' }}>{monthLabel}</span>
          <button style={navBtn} onClick={() => changeMonth(1)}>›</button>
        </div>
      }
    >
      <div style={grid.weekdays}>
        {WEEKDAYS.map(w => <div key={w} style={grid.weekdayLabel}>{w}</div>)}
      </div>
      <div style={grid.grid}>
        {cells.map((d, i) => {
          if (d === null) return <div key={i} />
          const dateStr = `${cursor.getFullYear()}-${pad(cursor.getMonth() + 1)}-${pad(d)}`
          const isSelected = dateStr === selectedDate
          const hasTask = daysWithTasks.has(dateStr)
          const isToday = dateStr === toISODate(today)
          return (
            <button
              key={i}
              onClick={() => setSelectedDate(dateStr)}
              style={{
                ...grid.day,
                ...(isSelected ? grid.daySelected : {}),
                ...(isToday && !isSelected ? grid.dayToday : {}),
              }}
            >
              {d}
              {hasTask && <span style={grid.dot} />}
            </button>
          )
        })}
      </div>

      <div style={{ marginTop: 18, paddingTop: 16, borderTop: '1px solid var(--panel-border)' }}>
        <div style={{ fontSize: 13, color: 'var(--flour-dim)', marginBottom: 10 }}>
          Tasks for {selectedLabel}
        </div>

        {tasksForSelected.length === 0 && (
          <div style={{ fontSize: 13, color: 'var(--flour-dim)', marginBottom: 12 }}>No tasks for this date.</div>
        )}

        <div style={{ display: 'grid', gap: 8, marginBottom: 14 }}>
          {tasksForSelected.map(t => (
            <div key={t.id} style={taskRow.row}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, cursor: 'pointer' }}>
                <input type="checkbox" checked={!!t.is_done} onChange={() => toggleDone(t)} />
                <span style={{ fontSize: 13, textDecoration: t.is_done ? 'line-through' : 'none', color: t.is_done ? 'var(--flour-dim)' : 'var(--flour)' }}>
                  {t.title}
                </span>
              </label>
              <button style={buttonDanger} onClick={() => removeTask(t.id)}>Delete</button>
            </div>
          ))}
        </div>

        <form onSubmit={handleAddTask} style={{ display: 'flex', gap: 8 }}>
          <input
            type="text" style={{ ...input, flex: 1 }} placeholder="Add a task…"
            value={newTitle} onChange={e => setNewTitle(e.target.value)}
          />
          <button type="submit" disabled={submitting} style={buttonPrimary}>+ Add</button>
        </form>
      </div>
    </Panel>
  )
}

const navBtn = {
  background: 'transparent',
  border: '1px solid var(--panel-border)',
  color: 'var(--flour)',
  borderRadius: 6,
  width: 26,
  height: 26,
  cursor: 'pointer',
  fontSize: 14,
}

const grid = {
  weekdays: { display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', marginBottom: 6 },
  weekdayLabel: { textAlign: 'center', fontSize: 11, color: 'var(--flour-dim)', textTransform: 'uppercase' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4 },
  day: {
    position: 'relative',
    aspectRatio: '1',
    background: 'transparent',
    border: 'none',
    color: 'var(--flour)',
    borderRadius: 8,
    cursor: 'pointer',
    fontSize: 13,
  },
  daySelected: {
    background: 'var(--amber)',
    color: 'var(--charcoal)',
    fontWeight: 600,
  },
  dayToday: {
    border: '1px solid var(--amber-bright)',
  },
  dot: {
    position: 'absolute',
    bottom: 4,
    left: '50%',
    transform: 'translateX(-50%)',
    width: 4,
    height: 4,
    borderRadius: '50%',
    background: 'var(--jam)',
  },
}

const taskRow = {
  row: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 10,
    padding: '6px 0',
  },
}
