import { useMetricsStore } from '../store/metricsStore'
import { useAlertStore } from '../store/alertStore'
import PageWrapper from '../components/layout/PageWrapper'
import AlertBanner from '../components/status/AlertBanner'
import StateIndicator from '../components/status/StateIndicator'
import MetricCard from '../components/status/MetricCard'
import MetricsLineChart from '../components/charts/MetricsLineChart'
import BrowningGauge from '../components/charts/BrowningGauge'
import AreaRiskChart from '../components/charts/AreaRiskChart'
import SmokeDensityChart from '../components/charts/SmokeDensityChart'
import EventLog from '../components/events/EventLog'

export default function Dashboard() {
  const { current, history, grillState } = useMetricsStore()
  const { alertHistory } = useAlertStore()

  const smokeLabel = !current ? '–'
    : current.smoke_density > 0.55 ? 'วิกฤต'
    : current.smoke_density > 0.30 ? 'ปานกลาง' : 'ต่ำ'

  const smokeColor = !current ? 'text-gray-400'
    : current.smoke_density > 0.55 ? 'text-red-500'
    : current.smoke_density > 0.30 ? 'text-yellow-500' : 'text-green-500'

  return (
    <PageWrapper title="แผงควบคุม">
      <AlertBanner />

      {/* สถานะ + คำอธิบาย */}
      <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm mb-4 flex items-start gap-4">
        <StateIndicator state={grillState} large />
        <p className="text-sm text-gray-600 leading-relaxed flex-1">
          {current?.explanation || 'เริ่มเซสชันจากหน้า ตรวจสอบสด หรือ อัปโหลด เพื่อเริ่มการวิเคราะห์'}
        </p>
      </div>

      {/* การ์ดสรุป */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <MetricCard label="L* (ความสว่าง)" value={current?.L_star_smooth ?? 0}
          color={current && current.L_star_smooth < 30 ? 'text-red-500' : 'text-blue-500'} />
        <MetricCard label="คะแนนการเกรียม" value={current?.browning_smooth ?? 0}
          color={current && current.browning_smooth > 0.72 ? 'text-orange-500' : 'text-yellow-500'} />
        <MetricCard label="ความเสี่ยงไหม้" value={current?.burn_risk_smooth ?? 0} unit="%"
          color={current && current.burn_risk_smooth > 10 ? 'text-red-500' : 'text-green-500'} />
        <MetricCard label="ความหนาแน่นควัน" value={smokeLabel}
          color={smokeColor}
          sub={current ? current.smoke_smooth.toFixed(3) : undefined} />
      </div>

      {/* แผนภูมิ */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <MetricsLineChart data={history} />
        <BrowningGauge value={current?.browning_smooth ?? 0} />
        <AreaRiskChart data={history} />
        <SmokeDensityChart data={history} />
      </div>

      {/* บันทึกเหตุการณ์ */}
      <EventLog events={alertHistory} />
    </PageWrapper>
  )
}
