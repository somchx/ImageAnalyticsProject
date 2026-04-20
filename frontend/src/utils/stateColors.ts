export const STATE_COLORS: Record<string, string> = {
  RAW: 'bg-gray-500 text-white',
  COOKING: 'bg-yellow-500 text-black',
  READY_TO_FLIP: 'bg-orange-400 text-black',
  READY: 'bg-green-500 text-white',
  OVERCOOKED_RISK: 'bg-orange-600 text-white',
  BURNT: 'bg-red-700 text-white',
}

export const STATE_BORDER: Record<string, string> = {
  RAW: 'border-gray-500',
  COOKING: 'border-yellow-500',
  READY_TO_FLIP: 'border-orange-400',
  READY: 'border-green-500',
  OVERCOOKED_RISK: 'border-orange-600',
  BURNT: 'border-red-700',
}

export const SEVERITY_COLORS: Record<string, string> = {
  WARNING: 'bg-yellow-600 text-white',
  CRITICAL: 'bg-red-700 text-white',
}
