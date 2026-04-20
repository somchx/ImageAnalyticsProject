import client from './client'
import { FrameMetrics, MetricsSummary } from '../types/metrics'

export const getMetrics = (sessionId: string, page = 0, limit = 500) =>
  client.get<FrameMetrics[]>(`/metrics/${sessionId}`, { params: { page, limit } }).then(r => r.data)

export const getMetricsSummary = (sessionId: string) =>
  client.get<MetricsSummary>(`/metrics/${sessionId}/summary`).then(r => r.data)
