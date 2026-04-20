import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, ResponsiveContainer
} from 'recharts'

interface Props {
  data: Array<{ frame_index: number; smoke_density: number }>
}

export default function SmokeDensityChart({ data }: Props) {
  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">ความหนาแน่นควันตามเวลา</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="frame_index" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
          <YAxis domain={[0, 1]} stroke="#9CA3AF" tick={{ fontSize: 10 }} />
          <Tooltip contentStyle={{ background: '#fff', border: '1px solid #E5E7EB', color: '#111827' }} />
          <ReferenceLine y={0.30} stroke="#F59E0B" strokeDasharray="4 2" label={{ value: 'แจ้งเตือน', fill: '#F59E0B', fontSize: 10 }} />
          <ReferenceLine y={0.55} stroke="#EF4444" strokeDasharray="4 2" label={{ value: 'วิกฤต', fill: '#EF4444', fontSize: 10 }} />
          <Line type="monotone" dataKey="smoke_density" name="ควัน" stroke="#8B5CF6" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
