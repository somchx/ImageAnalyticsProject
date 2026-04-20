import { STATE_COLORS } from '../../utils/stateColors'

const STATE_LABELS: Record<string, string> = {
  RAW: '🥩 ดิบ',
  COOKING: '🔥 กำลังปิ้ง',
  READY_TO_FLIP: '🔄 พลิกได้แล้ว',
  READY: '✅ สุกแล้ว',
  OVERCOOKED_RISK: '⚠️ เสี่ยงสุกเกิน',
  BURNT: '🚨 ไหม้',
}

interface Props {
  state: string
  large?: boolean
}

export default function StateIndicator({ state, large }: Props) {
  const cls = STATE_COLORS[state] || 'bg-gray-200 text-gray-700'
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full font-bold ${cls} ${large ? 'text-lg' : 'text-sm'}`}>
      {STATE_LABELS[state] || state}
    </span>
  )
}
