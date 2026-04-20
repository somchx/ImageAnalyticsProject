import { RadialBarChart, RadialBar, ResponsiveContainer, Tooltip } from 'recharts'

interface Props {
  value: number  // 0–1
}

export default function BrowningGauge({ value }: Props) {
  const pct = Math.round(value * 100)
  const color = value < 0.40 ? '#22C55E' : value < 0.65 ? '#F59E0B' : value < 0.85 ? '#F97316' : '#EF4444'
  const data = [{ name: 'การเกรียม', value: pct, fill: color }]

  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm flex flex-col items-center">
      <h3 className="text-sm font-semibold text-gray-700 mb-2 self-start">คะแนนการเกรียม</h3>
      <div className="relative w-full" style={{ height: 160 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%" cy="80%"
            innerRadius="60%" outerRadius="100%"
            startAngle={180} endAngle={0}
            data={data}
          >
            <RadialBar dataKey="value" cornerRadius={6} background={{ fill: '#E5E7EB' }} />
            <Tooltip
              contentStyle={{ background: '#fff', border: '1px solid #E5E7EB', color: '#111827' }}
              formatter={(v: number) => [`${v}%`, 'การเกรียม']}
            />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex items-end justify-center pb-2">
          <span className="text-2xl font-bold" style={{ color }}>{pct}%</span>
        </div>
      </div>
    </div>
  )
}
