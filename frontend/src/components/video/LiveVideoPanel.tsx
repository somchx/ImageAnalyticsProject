interface Props {
  b64?: string
  label: string
  placeholder?: string
}

export default function LiveVideoPanel({ b64, label, placeholder = 'รอรับเฟรม…' }: Props) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
      <div className="px-3 py-2 border-b border-gray-200 text-xs font-semibold text-gray-500">
        {label}
      </div>
      <div className="aspect-video bg-gray-100 flex items-center justify-center">
        {b64 ? (
          <img
            src={`data:image/jpeg;base64,${b64}`}
            alt={label}
            className="w-full h-full object-contain"
          />
        ) : (
          <p className="text-gray-400 text-sm">{placeholder}</p>
        )}
      </div>
    </div>
  )
}
