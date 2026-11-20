import { useEffect, useState } from 'react'
import { getOnlineOrderSummary, onlineOrdersSocketUrl } from '../api/client'

// One shared connection and poller, however many components show the count.
// New orders arrive instantly over a WebSocket; polling every 30 s is a backup.
let summary = { new: 0, active: 0 }
const listeners = new Set()
const eventListeners = new Set()
let timer = null
let socket = null
let retryDelay = 2000
let retryTimer = null
let pingTimer = null

async function poll() {
  try {
    summary = await getOnlineOrderSummary()
    listeners.forEach(fn => fn(summary))
  } catch {
    // backend asleep or offline; keep the last known numbers
  }
}

export function refreshOnlineOrderSummary() {
  return poll()
}

// ---- alerts: a short "ding" and a browser notification ----
const ALERTS_KEY = 'owner_order_alerts'
export const alertsEnabled = () => { try { return localStorage.getItem(ALERTS_KEY) === 'on' } catch { return false } }

export async function enableAlerts() {
  try { localStorage.setItem(ALERTS_KEY, 'on') } catch { /* ignore */ }
  playDing() // also unlocks sound: browsers only allow audio after a click
  if ('Notification' in window && Notification.permission === 'default') {
    await Notification.requestPermission()
  }
}
export function disableAlerts() {
  try { localStorage.removeItem(ALERTS_KEY) } catch { /* ignore */ }
}

let audioCtx = null
export function playDing() {
  try {
    audioCtx ||= new (window.AudioContext || window.webkitAudioContext)()
    const now = audioCtx.currentTime
    ;[[880, 0], [1320, 0.16]].forEach(([freq, delay]) => {
      const osc = audioCtx.createOscillator()
      const gain = audioCtx.createGain()
      osc.type = 'sine'
      osc.frequency.value = freq
      gain.gain.setValueAtTime(0.0001, now + delay)
      gain.gain.exponentialRampToValueAtTime(0.3, now + delay + 0.02)
      gain.gain.exponentialRampToValueAtTime(0.0001, now + delay + 0.5)
      osc.connect(gain).connect(audioCtx.destination)
      osc.start(now + delay)
      osc.stop(now + delay + 0.55)
    })
  } catch { /* sound not available */ }
}

function announce(event) {
  if (!alertsEnabled()) return
  playDing()
  if ('Notification' in window && Notification.permission === 'granted' && document.visibilityState !== 'visible') {
    const n = new Notification('New online order', {
      body: `${event.customer} ordered ₹${Math.round(event.total)} (${event.external_id})`,
      tag: event.external_id,
    })
    n.onclick = () => { window.focus(); window.location.assign('/online-orders') }
  }
}

function connect() {
  clearTimeout(retryTimer)
  try {
    socket = new WebSocket(onlineOrdersSocketUrl())
  } catch {
    return
  }
  socket.onopen = () => {
    retryDelay = 2000
    pingTimer = setInterval(() => socket?.readyState === 1 && socket.send('ping'), 25000)
  }
  socket.onmessage = msg => {
    let event
    try { event = JSON.parse(msg.data) } catch { return }
    if (event.type === 'new_order') announce(event)
    poll()
    eventListeners.forEach(fn => fn(event))
  }
  socket.onclose = e => {
    clearInterval(pingTimer)
    socket = null
    if (listeners.size === 0 || e.code === 4401) return // logged out or nobody listening
    retryTimer = setTimeout(connect, retryDelay)
    retryDelay = Math.min(retryDelay * 2, 60000) // back off while the server sleeps
  }
}

function start() {
  poll()
  timer = setInterval(poll, 30000)
  connect()
}

function stop() {
  clearInterval(timer)
  clearTimeout(retryTimer)
  timer = null
  if (socket) { socket.onclose = null; socket.close(); socket = null }
}

export function useOnlineOrderSummary() {
  const [value, setValue] = useState(summary)

  useEffect(() => {
    listeners.add(setValue)
    if (!timer) start()
    return () => {
      listeners.delete(setValue)
      if (listeners.size === 0) stop()
    }
  }, [])

  return value
}

// Run something whenever an order event arrives (new, accepted, cancelled…)
export function useOnlineOrderEvents(handler) {
  useEffect(() => {
    eventListeners.add(handler)
    return () => { eventListeners.delete(handler) }
  }, [handler])
}
