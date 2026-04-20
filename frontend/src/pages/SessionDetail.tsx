import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import PageWrapper from '../components/layout/PageWrapper'
import MetricsLineChart from '../components/charts/MetricsLineChart'
import AreaRiskChart from '../components/charts/AreaRiskChart'
import SmokeDensityChart from '../components/charts/SmokeDensityChart'
import BrowningGauge from '../components/charts/BrowningGauge'
import StateIndicator from '../components/status/StateIndicator'
import { getMetrics, getMetricsSummary } from '../api/metricsApi'
import { getEvents } from '../api/eventsApi'
import { downloadCsv } from '../api/exportApi'
import { FrameMetrics, MetricsSummary } from '../types/metrics'
import { GrillEvent } from '../types/events'
import { fmtTime } from '../utils/formatters'

export default function SessionDetail() {
  const { id } = useParams<{ id: string }>()
  const [metrics, setMetrics] = useState<FrameMetrics[]>([])
  const [summary, setSummary] = useState<MetricsSummary | null>(null)
  const [events, setEvents] = useState<GrillEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    Promise.all([
      getMetrics(id),
      getMetricsSummary(id).catch(() => null),
      getEvents(id).catch(() => []),
    ]).then(([m, s, e]) => {
      setMetrics(m)
      setSummary(s)
      setEvents(e)
    }).finally(() => setLoading(false))
  }, [id])

  const latestBrowning = metrics.length > 0 ? metrics[metrics.length - 1].browning_smooth : 0

  return (
    <PageWrapper
      title={`เซสชัน: ${id?.slice(0, 8)}…`}
      action={
        <button
          onClick={() => id && downloadCsv(id)}
          className="px-4 py-2 bg-orange-500 hover:bg-orange-600 rounded text-sm font-semibold text-white"
        >
          ส่งออก CSV
        </button>
      }
    >
      {loading ? (
        <p className="text-gray-500">กำลังโหลด…</p>
      ) : (
        <div className="space-y-4">
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'เฟรมทั้งหมด', value: summary.total_frames },
                { label: 'L* เฉลี่ย', value: summary.avg_L_star.toFixed(1) },
                { label: 'ความเสี่ยงไหม้สูงสุด', value: summary.max_burn_risk_pct.toFixed(1) + '%' },
                { label: 'สถานะสุดท้าย', value: summary.final_state || '–' },
              ].map(({ label, value }) => (
                <div key={label} className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
                  <p className="text-xs text-gray-500 mb-1">{label}</p>
                  <p className="text-xl font-bold text-gray-900">{value}</p>
                </div>
              ))}
            </div>
          )}

          {summary?.final_state && (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500">สถานะสุดท้าย:</span>
              <StateIndicator state={summary.final_state} large />
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <MetricsLineChart data={metrics} />
            <BrowningGauge value={latestBrowning} />
            <AreaRiskChart data={metrics} />
            <SmokeDensityChart data={metrics} />
          </div>

          {events.length > 0 && (
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-4 py-2 border-b border-gray-200">
                <h3 className="text-sm font-semibold text-gray-700">ลำดับเหตุการณ์</h3>
              </div>
              <div className="overflow-y-auto max-h-64">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="text-gray-500 border-b border-gray-200 bg-gray-50">
                      <th className="text-left px-4 py-2">เวลา</th>
                      <th className="text-left px-4 py-2">เฟรม</th>
                      <th className="text-left px-4 py-2">ประเภท</th>
                      <th className="text-left px-4 py-2">รหัส</th>
                      <th className="text-left px-4 py-2">ข้อความ</th>
                    </tr>
                  </thead>
                  <tbody>
                    {events.map(ev => (
                      <tr key={ev.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="px-4 py-2 text-gray-500">{fmtTime(ev.timestamp_ms)}</td>
                        <td className="px-4 py-2 text-gray-500">{ev.frame_index}</td>
                        <td className="px-4 py-2">
                          <span className={`px-1.5 py-0.5 rounded font-bold ${
                            ev.event_type === 'ALERT'
                              ? ev.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}>{ev.event_type === 'ALERT' ? 'แจ้งเตือน' : ev.event_type}</span>
                        </td>
                        <td className="px-4 py-2 font-mono text-gray-700">{ev.event_code}</td>
                        <td className="px-4 py-2 text-gray-600">{ev.message}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </PageWrapper>
  )
}
