export interface RawMetrics {
  L_star_mean: number
  L_star_std: number
  a_star_mean: number
  a_star_std: number
  b_star_mean: number
  b_star_std: number
  browning_score: number
  cooked_area_pct: number
  burn_risk_area_pct: number
  smoke_density: number
}

export interface SmoothedMetrics {
  L_star_smooth: number
  browning_smooth: number
  cooked_area_smooth: number
  burn_risk_smooth: number
  smoke_smooth: number
}

export interface FrameMetrics {
  id: number
  session_id: string
  frame_index: number
  timestamp_ms: number
  source_type: string
  L_star_mean: number
  L_star_std: number
  a_star_mean: number
  a_star_std: number
  b_star_mean: number
  b_star_std: number
  browning_score: number
  cooked_area_pct: number
  burn_risk_area_pct: number
  smoke_density: number
  L_star_smooth: number
  browning_smooth: number
  cooked_area_smooth: number
  burn_risk_smooth: number
  smoke_smooth: number
  grill_state: string
  state_changed: number
  alert_codes: string
  processing_time_ms: number
  explanation: string
}

export interface MetricsSummary {
  session_id: string
  total_frames: number
  avg_L_star: number
  min_L_star: number
  max_L_star: number
  avg_browning: number
  max_burn_risk_pct: number
  avg_smoke_density: number
  final_state: string | null
}
