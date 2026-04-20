import client from './client'
import { GrillEvent } from '../types/events'

export const getEvents = (sessionId: string) =>
  client.get<GrillEvent[]>(`/events/${sessionId}`).then(r => r.data)
