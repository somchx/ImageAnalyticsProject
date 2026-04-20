import { useEffect, useRef, useCallback } from 'react'
import { useSessionStore } from '../store/sessionStore'
import { useMetricsStore } from '../store/metricsStore'
import { useAlertStore } from '../store/alertStore'
import { WsMessage } from '../types/websocket'

export function useWebSocket(sessionId: string | null) {
  const wsRef = useRef<WebSocket | null>(null)
  const { setWsStatus } = useSessionStore()
  const { pushFrame } = useMetricsStore()
  const { addAlert } = useAlertStore()

  useEffect(() => {
    if (!sessionId) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const url = `${protocol}//${host}/ws/stream/${sessionId}`

    setWsStatus('CONNECTING')
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => setWsStatus('CONNECTED')
    ws.onclose = () => setWsStatus('DISCONNECTED')
    ws.onerror = () => setWsStatus('DISCONNECTED')

    ws.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data)
        if (msg.type === 'FRAME_RESULT') {
          const p = (msg as any).payload
          pushFrame({
            frame_index: p.frame_index,
            timestamp_ms: p.timestamp_ms,
            L_star_mean: p.raw_metrics.L_star_mean,
            a_star_mean: p.raw_metrics.a_star_mean,
            b_star_mean: p.raw_metrics.b_star_mean,
            browning_score: p.raw_metrics.browning_score,
            cooked_area_pct: p.raw_metrics.cooked_area_pct,
            burn_risk_area_pct: p.raw_metrics.burn_risk_area_pct,
            smoke_density: p.raw_metrics.smoke_density,
            L_star_smooth: p.smoothed_metrics.L_star_smooth,
            browning_smooth: p.smoothed_metrics.browning_smooth,
            cooked_area_smooth: p.smoothed_metrics.cooked_area_smooth,
            burn_risk_smooth: p.smoothed_metrics.burn_risk_smooth,
            smoke_smooth: p.smoothed_metrics.smoke_smooth,
            grill_state: p.grill_state,
            explanation: p.explanation,
            annotated_frame_b64: p.annotated_frame_b64,
            dehazed_frame_b64: p.dehazed_frame_b64,
          })
          for (const alert of p.alerts || []) {
            addAlert({
              id: `${Date.now()}-${alert.code}`,
              code: alert.code,
              severity: alert.severity,
              message: alert.message,
              timestamp: Date.now(),
              frame_index: p.frame_index,
              telegram_sent: alert.telegram_sent,
            })
          }
        } else if (msg.type === 'ALERT') {
          const p = (msg as any).payload
          addAlert({
            id: `${Date.now()}-${p.alert_code}`,
            code: p.alert_code,
            severity: p.severity,
            message: p.message,
            timestamp: Date.now(),
            frame_index: p.frame_index,
            telegram_sent: p.telegram_sent,
          })
        }
      } catch { /* ignore parse errors */ }
    }

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [sessionId])

  const sendFrame = useCallback((b64: string, sequence: number) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'FRAME_SUBMIT',
        payload: { frame_b64: b64, timestamp_ms: Date.now(), sequence },
      }))
    }
  }, [])

  const sendControl = useCallback((action: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'CONTROL', payload: { action } }))
    }
  }, [])

  return { sendFrame, sendControl }
}
