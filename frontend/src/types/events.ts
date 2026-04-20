export interface GrillEvent {
  id: number
  session_id: string
  frame_index: number
  timestamp_ms: number
  event_type: 'STATE_CHANGE' | 'ALERT'
  severity: 'WARNING' | 'CRITICAL' | null
  event_code: string
  from_state: string | null
  to_state: string | null
  trigger_metric: string | null
  trigger_value: number | null
  message: string
  metric_snapshot: string | null
  telegram_sent: number
}

export interface AlertItem {
  id: string
  code: string
  severity: 'WARNING' | 'CRITICAL'
  message: string
  timestamp: number
  frame_index?: number
  telegram_sent?: boolean
}
