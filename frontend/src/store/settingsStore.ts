import { create } from 'zustand'
import { ThresholdSettings } from '../types/settings'
import { getSettings, saveSettings } from '../api/settingsApi'

const DEFAULT: ThresholdSettings = {
  l_star_cooking_max: 65, l_star_ready_to_flip_max: 52,
  l_star_ready_max: 42, l_star_overcooked_max: 32, l_star_burnt_max: 22,
  browning_cooking_min: 0.15, browning_ready_to_flip_min: 0.40,
  browning_ready_min: 0.55, browning_overcooked_min: 0.72, browning_burnt_min: 0.88,
  burn_risk_warning_pct: 10, burn_risk_critical_pct: 20,
  smoke_warning_threshold: 0.30, smoke_critical_threshold: 0.55,
  smoothing_window: 7, alert_cooldown_seconds: 30, frame_sample_interval: 1,
  telegram_enabled: false, telegram_bot_token: '', telegram_chat_id: '',
}

interface SettingsState {
  settings: ThresholdSettings
  loading: boolean
  fetch: () => Promise<void>
  save: (data: ThresholdSettings) => Promise<void>
}

export const useSettingsStore = create<SettingsState>((set) => ({
  settings: DEFAULT,
  loading: false,
  fetch: async () => {
    set({ loading: true })
    try {
      const data = await getSettings()
      set({ settings: data })
    } finally {
      set({ loading: false })
    }
  },
  save: async (data) => {
    set({ loading: true })
    try {
      const saved = await saveSettings(data)
      set({ settings: saved })
    } finally {
      set({ loading: false })
    }
  },
}))
