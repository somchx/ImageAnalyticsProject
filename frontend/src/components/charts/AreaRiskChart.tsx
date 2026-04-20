import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

interface Props {
  data: Array<{ frame_index: number; cooked_area_pct: number; burn_risk_area_pct: number }>
}

export default function AreaRiskChart({ data }: Props) {
  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">พื้นที่สุก vs พื้นที่เสี่ยงไหม้ (%)</h3>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis dataKey="frame_index" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
          <YAxis domain={[0, 100]} stroke="#9CA3AF" tick={{ fontSize: 10 }} unit="%" />
          <Tooltip
            contentStyle={{ background: '#fff', border: '1px solid #E5E7EB', color: '#111827' }}
            formatter={(v: number) => [`${v.toFixed(1)}%`]}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Area type="monotone" dataKey="cooked_area_pct" name="สุก" stackId="1"
            stroke="#22C55E" fill="#22C55E" fillOpacity={0.3} />
          <Area type="monotone" dataKey="burn_risk_area_pct" name="เสี่ยงไหม้" stackId="1"
            stroke="#EF4444" fill="#EF4444" fillOpacity={0.4} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
