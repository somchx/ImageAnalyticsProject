import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

interface Props {
  data: Array<{ frame_index: number; L_star_mean: number; a_star_mean: number; b_star_mean: number }>
}

export default function MetricsLineChart({ data }: Props) {
  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">ค่า CIE L*a*b* ตามเวลา</h3>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="frame_index" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
          <YAxis stroke="#9CA3AF" tick={{ fontSize: 10 }} />
          <Tooltip contentStyle={{ background: '#fff', border: '1px solid #E5E7EB', color: '#111827' }} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line type="monotone" dataKey="L_star_mean" name="L*" stroke="#3B82F6" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="a_star_mean" name="a*" stroke="#EF4444" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="b_star_mean" name="b*" stroke="#F59E0B" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
