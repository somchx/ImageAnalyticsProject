import { create } from 'zustand'

type WsStatus = 'DISCONNECTED' | 'CONNECTING' | 'CONNECTED'

interface SessionState {
  activeSessionId: string | null
  wsStatus: WsStatus
  isProcessing: boolean
  setActiveSession: (id: string | null) => void
  setWsStatus: (status: WsStatus) => void
  setProcessing: (v: boolean) => void
}

export const useSessionStore = create<SessionState>((set) => ({
  activeSessionId: null,
  wsStatus: 'DISCONNECTED',
  isProcessing: false,
  setActiveSession: (id) => set({ activeSessionId: id }),
  setWsStatus: (status) => set({ wsStatus: status }),
  setProcessing: (v) => set({ isProcessing: v }),
}))
