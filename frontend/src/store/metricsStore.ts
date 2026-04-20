import { create } from 'zustand'

interface LiveFrame {
  frame_index: number
  timestamp_ms: number
  L_star_mean: number
  a_star_mean: number
  b_star_mean: number
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
  explanation: string
  annotated_frame_b64: string
  dehazed_frame_b64: string
}

interface MetricsState {
  current: LiveFrame | null
  history: LiveFrame[]
  grillState: string
  pushFrame: (frame: LiveFrame) => void
  reset: () => void
}

const MAX_HISTORY = 200

export const useMetricsStore = create<MetricsState>((set) => ({
  current: null,
  history: [],
  grillState: 'RAW',
  pushFrame: (frame) =>
    set((s) => {
      const history = [...s.history, frame].slice(-MAX_HISTORY)
      return { current: frame, history, grillState: frame.grill_state }
    }),
  reset: () => set({ current: null, history: [], grillState: 'RAW' }),
}))
