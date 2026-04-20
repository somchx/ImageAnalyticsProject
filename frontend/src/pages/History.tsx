import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PageWrapper from '../components/layout/PageWrapper'
import { listSessions } from '../api/sessionApi'
import { Session } from '../types/session'
import StateIndicator from '../components/status/StateIndicator'
import { fmtTime } from '../utils/formatters'

export default function History() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    listSessions().then(setSessions).finally(() => setLoading(false))
  }, [])

  return (
    <PageWrapper title="ประวัติการวิเคราะห์">
      {loading ? (
        <p className="text-gray-500">กำลังโหลด…</p>
      ) : sessions.length === 0 ? (
        <p className="text-gray-500">ยังไม่มีเซสชัน เริ่มจากหน้าตรวจสอบสดหรืออัปโหลด</p>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 border-b border-gray-200 text-xs uppercase bg-gray-50">
                <th className="text-left px-4 py-3">รหัส</th>
                <th className="text-left px-4 py-3">ชื่อ</th>
                <th className="text-left px-4 py-3">ประเภท</th>
                <th className="text-left px-4 py-3">สร้างเมื่อ</th>
                <th className="text-left px-4 py-3">เฟรม</th>
                <th className="text-left px-4 py-3">สถานะสุดท้าย</th>
                <th className="text-left px-4 py-3">สถานะ</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody>
              {sessions.map(s => (
                <tr key={s.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-gray-400 text-xs">{s.id.slice(0, 8)}…</td>
                  <td className="px-4 py-3 text-gray-900">{s.name}</td>
                  <td className="px-4 py-3 text-gray-600">{s.source_type}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{fmtTime(s.created_at)}</td>
                  <td className="px-4 py-3 text-gray-600">{s.total_frames}</td>
                  <td className="px-4 py-3">
                    {s.final_state ? <StateIndicator state={s.final_state} /> : <span className="text-gray-400">–</span>}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      s.status === 'ACTIVE' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                    }`}>{s.status === 'ACTIVE' ? 'กำลังใช้งาน' : 'เสร็จสิ้น'}</span>
                  </td>
                  <td className="px-4 py-3">
                    <Link to={`/history/${s.id}`}
                      className="text-orange-500 hover:text-orange-600 text-xs font-medium">
                      ดูรายละเอียด →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PageWrapper>
  )
}
