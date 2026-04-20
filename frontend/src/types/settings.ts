export interface ThresholdSettings {
  l_star_cooking_max: number
  l_star_ready_to_flip_max: number
  l_star_ready_max: number
  l_star_overcooked_max: number
  l_star_burnt_max: number
  browning_cooking_min: number
  browning_ready_to_flip_min: number
  browning_ready_min: number
  browning_overcooked_min: number
  browning_burnt_min: number
  burn_risk_warning_pct: number
  burn_risk_critical_pct: number
  smoke_warning_threshold: number
  smoke_critical_threshold: number
  smoothing_window: number
  alert_cooldown_seconds: number
  frame_sample_interval: number
  telegram_enabled: boolean
  telegram_bot_token: string
  telegram_chat_id: string
}
