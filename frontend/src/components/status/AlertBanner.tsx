import { useAlertStore } from '../../store/alertStore'
import { AlertItem } from '../../types/events'
import { X } from 'lucide-react'

function Banner({ alert }: { alert: AlertItem }) {
  const { dismissAlert } = useAlertStore()
  const bg = alert.severity === 'CRITICAL' ? 'bg-red-700' : 'bg-yellow-600'

  return (
    <div className={`${bg} text-white px-4 py-2 rounded flex items-center justify-between gap-4 shadow-lg`}>
      <div>
        <span className="font-bold text-sm">{alert.code.replace(/_/g, ' ')}</span>
        <span className="mx-2 text-white/60">·</span>
        <span className="text-sm">{alert.message}</span>
        {alert.telegram_sent && (
          <span className="ml-2 text-xs bg-white/20 px-1.5 py-0.5 rounded">📱 ส่ง Telegram แล้ว</span>
        )}
      </div>
      <button onClick={() => dismissAlert(alert.id)} className="flex-shrink-0 hover:opacity-70">
        <X className="w-4 h-4" />
      </button>
    </div>
  )
}

export default function AlertBanner() {
  const { activeAlerts } = useAlertStore()
  if (!activeAlerts.length) return null

  return (
    <div className="space-y-2 mb-4">
      {activeAlerts.slice(0, 4).map(alert => (
        <Banner key={alert.id} alert={alert} />
      ))}
    </div>
  )
}
