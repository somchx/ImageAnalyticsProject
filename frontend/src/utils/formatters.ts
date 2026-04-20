export function fmt2(n: number) {
  return n.toFixed(2)
}

export function fmt1(n: number) {
  return n.toFixed(1)
}

export function fmtTime(ms: number) {
  const d = new Date(ms)
  return d.toLocaleTimeString()
}

export function fmtElapsed(startMs: number) {
  const s = Math.floor((Date.now() - startMs) / 1000)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`
}
