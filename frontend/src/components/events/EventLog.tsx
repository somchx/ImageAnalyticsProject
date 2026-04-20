import { AlertItem } from '../../types/events'
import { fmtTime } from '../../utils/formatters'
import { SEVERITY_COLORS } from '../../utils/stateColors'

const SEVERITY_LABELS: Record<string, string> = {
  WARNING: 'แจ้งเตือน',
  CRITICAL: 'วิกฤต',
}

interface Props {
  events: AlertItem[]
  maxRows?: number
}

export default function EventLog({ events, maxRows = 50 }: Props) {
  const rows = events.slice(0, maxRows)

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
      <div className="px-4 py-2 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-700">บันทึกเหตุการณ์</h3>
      </div>
      <div className="overflow-y-auto max-h-56">
        {rows.length === 0 ? (
          <p className="text-gray-400 text-sm px-4 py-3">ยังไม่มีเหตุการณ์</p>
        ) : (
          <table className="w-full text-xs">
            <thead>
              <tr className="text-gray-500 border-b border-gray-200 bg-gray-50">
                <th className="text-left px-4 py-2">เวลา</th>
                <th className="text-left px-4 py-2">รหัส</th>
                <th className="text-left px-4 py-2">ระดับ</th>
                <th className="text-left px-4 py-2">ข้อความ</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(ev => (
                <tr key={ev.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-1.5 text-gray-500 whitespace-nowrap">{fmtTime(ev.timestamp)}</td>
                  <td className="px-4 py-1.5 font-mono text-gray-700">{ev.code}</td>
                  <td className="px-4 py-1.5">
                    <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${SEVERITY_COLORS[ev.severity] || 'bg-gray-200 text-gray-700'}`}>
                      {SEVERITY_LABELS[ev.severity] || ev.severity}
                    </span>
                  </td>
                  <td className="px-4 py-1.5 text-gray-600">{ev.message}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
