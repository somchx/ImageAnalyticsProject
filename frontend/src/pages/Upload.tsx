import { useState, useRef } from 'react'
import PageWrapper from '../components/layout/PageWrapper'
import StateIndicator from '../components/status/StateIndicator'
import { uploadImage, uploadVideo } from '../api/uploadApi'
import { Upload as UploadIcon } from 'lucide-react'

interface ImageResult {
  session_id: string
  grill_state: string
  explanation: string
  raw_metrics: {
    L_star_mean: number; a_star_mean: number; b_star_mean: number
    browning_score: number; cooked_area_pct: number; burn_risk_area_pct: number
    smoke_density: number
  }
  annotated_frame_b64: string
  alerts: Array<{ code: string; severity: string; message: string }>
}

export default function UploadPage() {
  const [loading, setLoading] = useState(false)
  const [imageResult, setImageResult] = useState<ImageResult | null>(null)
  const [videoSessionId, setVideoSessionId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleFile = async (file: File) => {
    setError(null)
    setImageResult(null)
    setVideoSessionId(null)
    setLoading(true)
    try {
      const isVideo = file.type.startsWith('video/')
      if (isVideo) {
        const res = await uploadVideo(file)
        setVideoSessionId(res.session_id)
      } else {
        const res: ImageResult = await uploadImage(file)
        setImageResult(res)
      }
    } catch (e: any) {
      setError(e?.message || 'อัปโหลดล้มเหลว')
    } finally {
      setLoading(false)
    }
  }

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  return (
    <PageWrapper title="อัปโหลดวิเคราะห์">
      {/* Drop zone */}
      <div
        onDrop={onDrop}
        onDragOver={e => e.preventDefault()}
        onClick={() => inputRef.current?.click()}
        className="border-2 border-dashed border-gray-300 hover:border-orange-400 rounded-xl p-12
          flex flex-col items-center justify-center cursor-pointer transition-colors mb-6 bg-white"
      >
        <UploadIcon className="w-10 h-10 text-gray-400 mb-3" />
        <p className="text-gray-700 font-medium">วางไฟล์รูปภาพหรือวิดีโอที่นี่ หรือคลิกเพื่อเลือกไฟล์</p>
        <p className="text-gray-400 text-sm mt-1">รองรับ JPG, PNG, MP4, AVI, MOV</p>
        <input
          ref={inputRef}
          type="file"
          accept="image/*,video/*"
          className="hidden"
          onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
      </div>

      {loading && (
        <div className="text-center py-10 text-gray-500">
          <div className="animate-spin w-8 h-8 border-2 border-orange-400 border-t-transparent rounded-full mx-auto mb-3" />
          กำลังประมวลผล…
        </div>
      )}

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      {videoSessionId && (
        <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <p className="text-green-600 font-semibold mb-1">วิดีโอกำลังประมวลผลในเบื้องหลัง</p>
          <p className="text-gray-600 text-sm">รหัสเซสชัน: <code className="text-orange-500">{videoSessionId}</code></p>
          <p className="text-gray-400 text-xs mt-2">
            เชื่อมต่อ WebSocket หรือตรวจสอบที่หน้าประวัติ → {videoSessionId.slice(0,8)} เพื่อดูผลลัพธ์
          </p>
        </div>
      )}

      {imageResult && (
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <StateIndicator state={imageResult.grill_state} large />
            <div className="bg-white rounded-lg p-3 border border-gray-200 shadow-sm flex-1">
              <p className="text-xs text-gray-500 mb-1">คำอธิบาย</p>
              <p className="text-sm text-gray-700">{imageResult.explanation}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-lg overflow-hidden border border-gray-200 shadow-sm">
              <p className="text-xs text-gray-500 px-3 py-2 border-b border-gray-200">ผลลัพธ์ที่มีคำอธิบาย</p>
              <img
                src={`data:image/jpeg;base64,${imageResult.annotated_frame_b64}`}
                alt="ผลลัพธ์"
                className="w-full object-contain"
              />
            </div>

            <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
              <p className="text-sm font-semibold text-gray-700 mb-3">ค่าตัวชี้วัด</p>
              <div className="space-y-2 text-sm">
                {Object.entries(imageResult.raw_metrics).map(([k, v]) => (
                  <div key={k} className="flex justify-between">
                    <span className="text-gray-500">{k.replace(/_/g, ' ')}</span>
                    <span className="font-mono text-gray-900">{Number(v).toFixed(3)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {imageResult.alerts.length > 0 && (
            <div className="space-y-2">
              {imageResult.alerts.map((a, i) => (
                <div key={i}
                  className={`px-4 py-2 rounded text-sm font-medium ${
                    a.severity === 'CRITICAL' ? 'bg-red-100 text-red-700 border border-red-200' : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                  }`}>
                  [{a.code}] {a.message}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </PageWrapper>
  )
}
