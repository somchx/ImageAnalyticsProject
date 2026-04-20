interface Props {
  label: string
  name: string
  value: number
  min: number
  max: number
  step?: number
  onChange: (name: string, value: number) => void
}

export default function ThresholdSlider({ label, name, value, min, max, step = 1, onChange }: Props) {
  return (
    <div className="flex items-center gap-4">
      <label className="text-sm text-gray-700 w-52 flex-shrink-0">{label}</label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={e => onChange(name, parseFloat(e.target.value))}
        className="flex-1 accent-orange-500"
      />
      <span className="text-sm font-mono text-orange-500 w-14 text-right">
        {Number.isInteger(step) ? value : value.toFixed(2)}
      </span>
    </div>
  )
}
