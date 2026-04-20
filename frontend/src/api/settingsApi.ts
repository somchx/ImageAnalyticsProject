import client from './client'
import { ThresholdSettings } from '../types/settings'

export const getSettings = () => client.get<ThresholdSettings>('/settings').then(r => r.data)
export const saveSettings = (data: ThresholdSettings) =>
  client.put<ThresholdSettings>('/settings', data).then(r => r.data)
export const testTelegram = () =>
  client.post('/notifications/telegram/test').then(r => r.data)
