import client from './client'
import { Session } from '../types/session'

export const listSessions = () => client.get<Session[]>('/sessions').then(r => r.data)
export const getSession = (id: string) => client.get<Session>(`/sessions/${id}`).then(r => r.data)
export const createSession = (name: string, source_type: string) =>
  client.post<Session>('/sessions', { name, source_type }).then(r => r.data)
export const closeSession = (id: string) =>
  client.patch<Session>(`/sessions/${id}/close`).then(r => r.data)
