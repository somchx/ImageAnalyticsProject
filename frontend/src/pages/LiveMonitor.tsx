import { useState, useCallback } from 'react'
import PageWrapper from '../components/layout/PageWrapper'
import LiveVideoPanel from '../components/video/LiveVideoPanel'
import AlertBanner from '../components/status/AlertBanner'
import StateIndicator from '../components/status/StateIndicator'
import { useWebSocket } from '../hooks/useWebSocket'
import { useWebcam } from '../hooks/useWebcam'
import { useMetricsStore } from '../store/metricsStore'
import { useSessionStore } from '../store/sessionStore'
import { createSession } from '../api/sessionApi'
import { fmt1, fmt2 } from '../utils/formatters'

export default function LiveMonitor() {
  const { current, grillState } = useMetricsStore()
  const { activeSessionId, setActiveSession, setProcessing, isProcessing } = useSessionStore()
  const [sessionId, setSessionId] = useState<string | null>(null)

  const { sendFrame } = useWebSocket(sessionId)

  const onFrame = useCallback((b64: string, seq: number) => {
    sendFrame(b64, seq)
  }, [sendFrame])

  const { videoRef, active, start, stop } = useWebcam(onFrame, 1000)

  const handleStart = async () => {
    const s = await createSession('Webcam Session', 'WEBCAM')
    setActiveSession(s.id)
    setSessionId(s.id)
    setProcessing(true)
    await start()
  }

  const handleStop = () => {
    stop()
    setProcessing(false)
  }

  return (
    <PageWrapper title="ตรวจสอบสด">
      <AlertBanner />

      {/* Controls */}
      <div className="flex items-center gap-4 mb-4">
        {!active ? (
          <button
            onClick={handleStart}
            className="px-5 py-2 bg-orange-500 hover:bg-orange-600 rounded-lg font-semibold text-white text-sm"
          >
            เปิดกล้อง
          </button>
        ) : (
          <button
            onClick={handleStop}
            className="px-5 py-2 bg-red-600 hover:bg-red-700 rounded-lg font-semibold text-white text-sm"
          >
            หยุด
          </button>
        )}
        {active && <StateIndicator state={grillState} />}
        {sessionId && (
          <span className="text-xs text-gray-500 font-mono">
            เซสชัน: {sessionId.slice(0, 8)}…
          </span>
        )}
      </div>

      {/* Video panels */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        {/* Live webcam preview */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-3 py-2 border-b border-gray-200 text-xs font-semibold text-gray-500">
            ภาพจากกล้องสด
          </div>
          <div className="aspect-video bg-gray-100 flex items-center justify-center">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-contain"
            />
          </div>
        </div>

        <LiveVideoPanel
          b64={current?.annotated_frame_b64}
          label="ภาพที่ประมวลผลแล้ว"
        />
        <LiveVideoPanel
          b64={current?.dehazed_frame_b64}
          label="ภาพลดหมอก (DCP)"
        />
      </div>

      {/* Explanation box */}
      <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm mb-4">
        <p className="text-xs font-semibold text-gray-500 mb-1">คำอธิบายผลลัพธ์</p>
        <p className="text-sm text-gray-700 leading-relaxed">
          {current?.explanation || 'ยังไม่มีเฟรมที่ประมวลผล'}
        </p>
      </div>

      {/* Live metrics */}
      {current && (
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {[
            { label: 'L*', value: fmt1(current.L_star_smooth) },
            { label: 'a*', value: fmt1(current.a_star_mean) },
            { label: 'b*', value: fmt1(current.b_star_mean) },
            { label: 'การเกรียม', value: fmt2(current.browning_smooth) },
            { label: 'สุก %', value: fmt1(current.cooked_area_smooth) + '%' },
            { label: 'เสี่ยงไหม้ %', value: fmt1(current.burn_risk_smooth) + '%' },
          ].map(({ label, value }) => (
            <div key={label} className="bg-white rounded p-3 border border-gray-200 shadow-sm text-center">
              <p className="text-xs text-gray-500">{label}</p>
              <p className="text-lg font-bold text-gray-900">{value}</p>
            </div>
          ))}
        </div>
      )}
    </PageWrapper>
  )
}
