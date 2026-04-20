import { RawMetrics, SmoothedMetrics } from './metrics'

export interface WsFrameResult {
  type: 'FRAME_RESULT'
  payload: {
    session_id: string
    frame_index: number
    timestamp_ms: number
    raw_metrics: RawMetrics
    smoothed_metrics: SmoothedMetrics
    grill_state: string
    prev_state: string
    state_changed: boolean
    annotated_frame_b64: string
    dehazed_frame_b64: string
    roi_mask_b64: string
    explanation: string
    processing_time_ms: number
    alerts: Array<{ code: string; severity: string; message: string; telegram_sent: boolean }>
  }
}

export interface WsAlert {
  type: 'ALERT'
  payload: {
    session_id: string
    alert_code: string
    severity: string
    message: string
    telegram_sent: boolean
    frame_index: number
  }
}

export interface WsStateChange {
  type: 'STATE_CHANGE'
  payload: {
    session_id: string
    from_state: string
    to_state: string
    frame_index: number
  }
}

export type WsMessage = WsFrameResult | WsAlert | WsStateChange | { type: string; payload: any }
