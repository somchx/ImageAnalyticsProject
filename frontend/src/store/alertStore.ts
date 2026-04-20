import { create } from 'zustand'
import { AlertItem } from '../types/events'

interface AlertState {
  activeAlerts: AlertItem[]
  alertHistory: AlertItem[]
  addAlert: (alert: AlertItem) => void
  dismissAlert: (id: string) => void
  clearAll: () => void
}

export const useAlertStore = create<AlertState>((set) => ({
  activeAlerts: [],
  alertHistory: [],
  addAlert: (alert) =>
    set((s) => ({
      activeAlerts: [alert, ...s.activeAlerts].slice(0, 10),
      alertHistory: [alert, ...s.alertHistory].slice(0, 200),
    })),
  dismissAlert: (id) =>
    set((s) => ({ activeAlerts: s.activeAlerts.filter((a) => a.id !== id) })),
  clearAll: () => set({ activeAlerts: [] }),
}))
