interface Props {
  label: string
  value: string | number
  unit?: string
  color?: string
  sub?: string
}

export default function MetricCard({ label, value, unit = '', color = 'text-gray-900', sub }: Props) {
  return (
    <div className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>
        {typeof value === 'number' ? value.toFixed(2) : value}
        {unit && <span className="text-sm font-normal text-gray-400 ml-1">{unit}</span>}
      </p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}
