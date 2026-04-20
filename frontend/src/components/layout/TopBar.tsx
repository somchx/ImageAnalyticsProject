import { useSessionStore } from '../../store/sessionStore'
import { useMetricsStore } from '../../store/metricsStore'
import { STATE_COLORS } from '../../utils/stateColors'

const WS_LABELS: Record<string, string> = {
  CONNECTED: 'เชื่อมต่อแล้ว',
  CONNECTING: 'กำลังเชื่อมต่อ',
  DISCONNECTED: 'ไม่ได้เชื่อมต่อ',
}

export default function TopBar() {
  const { wsStatus, activeSessionId } = useSessionStore()
  const { grillState } = useMetricsStore()

  const wsColor = wsStatus === 'CONNECTED' ? 'bg-green-500' :
    wsStatus === 'CONNECTING' ? 'bg-yellow-400' : 'bg-gray-400'

  return (
    <header className="h-12 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <div className="text-sm text-gray-500">
        {activeSessionId ? (
          <span>เซสชัน: <code className="text-orange-500">{activeSessionId.slice(0, 8)}…</code></span>
        ) : (
          <span>ไม่มีเซสชันที่กำลังใช้งาน</span>
        )}
      </div>
      <div className="flex items-center gap-4">
        {activeSessionId && (
          <span className={`text-xs font-bold px-2 py-0.5 rounded ${STATE_COLORS[grillState] || 'bg-gray-200 text-gray-700'}`}>
            {grillState}
          </span>
        )}
        <div className="flex items-center gap-1.5 text-xs text-gray-500">
          <span className={`w-2 h-2 rounded-full ${wsColor}`} />
          {WS_LABELS[wsStatus] || wsStatus}
        </div>
      </div>
    </header>
  )
}
