import { useEffect, useState } from 'react'
import PageWrapper from '../components/layout/PageWrapper'
import ThresholdSlider from '../components/settings/ThresholdSlider'
import { useSettingsStore } from '../store/settingsStore'
import { ThresholdSettings } from '../types/settings'
import { testTelegram } from '../api/settingsApi'

export default function Settings() {
  const { settings, loading, fetch, save } = useSettingsStore()
  const [local, setLocal] = useState<ThresholdSettings>(settings)
  const [saved, setSaved] = useState(false)
  const [testResult, setTestResult] = useState<string | null>(null)

  useEffect(() => { fetch() }, [])
  useEffect(() => { setLocal(settings) }, [settings])

  const onChange = (name: string, value: number | boolean | string) => {
    setLocal(prev => ({ ...prev, [name]: value }))
    setSaved(false)
  }

  const handleSave = async () => {
    await save(local)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const handleTestTelegram = async () => {
    const res = await testTelegram()
    setTestResult(res.success ? '✅ Test message sent!' : '❌ Failed — check token and chat_id')
    setTimeout(() => setTestResult(null), 5000)
  }

  const Section = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <div className="bg-white rounded-lg p-5 border border-gray-200 shadow-sm mb-4">
      <h3 className="text-sm font-bold text-gray-700 mb-4 uppercase tracking-wide">{title}</h3>
      <div className="space-y-4">{children}</div>
    </div>
  )

  return (
    <PageWrapper
      title="ตั้งค่า"
      action={
        <button
          onClick={handleSave}
          disabled={loading}
          className="px-5 py-2 bg-orange-500 hover:bg-orange-600 disabled:opacity-50 rounded-lg font-semibold text-white text-sm"
        >
          {loading ? 'กำลังบันทึก…' : saved ? '✓ บันทึกแล้ว' : 'บันทึกการตั้งค่า'}
        </button>
      }
    >
      <Section title="ค่าขีดจำกัด CIE L*">
        <ThresholdSlider label="L* สูงสุดเพื่อเริ่มปิ้ง (COOKING)" name="l_star_cooking_max"
          value={local.l_star_cooking_max} min={40} max={90} onChange={onChange} />
        <ThresholdSlider label="L* สูงสุดพร้อมพลิก (READY_TO_FLIP)" name="l_star_ready_to_flip_max"
          value={local.l_star_ready_to_flip_max} min={30} max={70} onChange={onChange} />
        <ThresholdSlider label="L* สูงสุดสุกแล้ว (READY)" name="l_star_ready_max"
          value={local.l_star_ready_max} min={20} max={60} onChange={onChange} />
        <ThresholdSlider label="L* สูงสุดเสี่ยงสุกเกิน (OVERCOOKED_RISK)" name="l_star_overcooked_max"
          value={local.l_star_overcooked_max} min={15} max={50} onChange={onChange} />
        <ThresholdSlider label="L* สูงสุดไหม้ (BURNT)" name="l_star_burnt_max"
          value={local.l_star_burnt_max} min={5} max={35} onChange={onChange} />
      </Section>

      <Section title="ค่าขีดจำกัดคะแนนการเกรียม">
        <ThresholdSlider label="การเกรียมต่ำสุดเริ่มปิ้ง (COOKING)" name="browning_cooking_min"
          value={local.browning_cooking_min} min={0.0} max={0.5} step={0.01} onChange={onChange} />
        <ThresholdSlider label="การเกรียมต่ำสุดพร้อมพลิก (READY_TO_FLIP)" name="browning_ready_to_flip_min"
          value={local.browning_ready_to_flip_min} min={0.1} max={0.7} step={0.01} onChange={onChange} />
        <ThresholdSlider label="การเกรียมต่ำสุดสุกแล้ว (READY)" name="browning_ready_min"
          value={local.browning_ready_min} min={0.2} max={0.8} step={0.01} onChange={onChange} />
        <ThresholdSlider label="การเกรียมต่ำสุดเสี่ยงสุกเกิน (OVERCOOKED_RISK)" name="browning_overcooked_min"
          value={local.browning_overcooked_min} min={0.3} max={0.95} step={0.01} onChange={onChange} />
        <ThresholdSlider label="การเกรียมต่ำสุดไหม้ (BURNT)" name="browning_burnt_min"
          value={local.browning_burnt_min} min={0.5} max={1.0} step={0.01} onChange={onChange} />
      </Section>

      <Section title="ค่าขีดจำกัดความเสี่ยงไหม้">
        <ThresholdSlider label="ความเสี่ยงไหม้ระดับแจ้งเตือน (%)" name="burn_risk_warning_pct"
          value={local.burn_risk_warning_pct} min={2} max={30} onChange={onChange} />
        <ThresholdSlider label="ความเสี่ยงไหม้ระดับวิกฤต (%)" name="burn_risk_critical_pct"
          value={local.burn_risk_critical_pct} min={5} max={50} onChange={onChange} />
      </Section>

      <Section title="ค่าขีดจำกัดควัน">
        <ThresholdSlider label="ควันระดับแจ้งเตือน" name="smoke_warning_threshold"
          value={local.smoke_warning_threshold} min={0.1} max={0.7} step={0.01} onChange={onChange} />
        <ThresholdSlider label="ควันระดับวิกฤต" name="smoke_critical_threshold"
          value={local.smoke_critical_threshold} min={0.2} max={1.0} step={0.01} onChange={onChange} />
      </Section>

      <Section title="ระบบ">
        <ThresholdSlider label="หน้าต่างปรับค่าเรียบ (เฟรม)" name="smoothing_window"
          value={local.smoothing_window} min={1} max={30} onChange={onChange} />
        <ThresholdSlider label="ระยะเวลาพักการแจ้งเตือน (วินาที)" name="alert_cooldown_seconds"
          value={local.alert_cooldown_seconds} min={5} max={180} onChange={onChange} />
        <ThresholdSlider label="ช่วงเวลาสุ่มเฟรม" name="frame_sample_interval"
          value={local.frame_sample_interval} min={1} max={30} onChange={onChange} />
      </Section>

      <Section title="การแจ้งเตือนผ่าน Telegram">
        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="tg-enabled"
            checked={local.telegram_enabled}
            onChange={e => onChange('telegram_enabled', e.target.checked)}
            className="accent-orange-400 w-4 h-4"
          />
          <label htmlFor="tg-enabled" className="text-sm text-gray-700">เปิดใช้การแจ้งเตือน Telegram</label>
        </div>
        <div className="space-y-2">
          <div className="flex items-center gap-4">
            <label className="text-sm text-gray-700 w-40">Bot Token</label>
            <input
              type="password"
              value={local.telegram_bot_token}
              onChange={e => onChange('telegram_bot_token', e.target.value)}
              placeholder="123456:ABC-DEF..."
              className="flex-1 bg-white text-gray-900 rounded px-3 py-1.5 text-sm border border-gray-300 focus:border-orange-400 outline-none"
            />
          </div>
          <div className="flex items-center gap-4">
            <label className="text-sm text-gray-700 w-40">Chat ID</label>
            <input
              type="text"
              value={local.telegram_chat_id}
              onChange={e => onChange('telegram_chat_id', e.target.value)}
              placeholder="-100123456789"
              className="flex-1 bg-white text-gray-900 rounded px-3 py-1.5 text-sm border border-gray-300 focus:border-orange-400 outline-none"
            />
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleTestTelegram}
            className="px-4 py-1.5 bg-blue-500 hover:bg-blue-600 rounded text-sm font-medium text-white"
          >
            ส่งข้อความทดสอบ
          </button>
          {testResult && <span className="text-sm text-gray-700">{testResult}</span>}
        </div>
      </Section>

      <Section title="LINE Messaging API (เร็วๆ นี้)">
        <p className="text-xs text-gray-500">
          การรวม LINE เตรียมไว้แล้วในรูปแบบ stub ตั้งค่า LINE_CHANNEL_ACCESS_TOKEN และ LINE_USER_ID
          แล้วพัฒนา <code>line_service.py</code> เพื่อเปิดใช้งาน
        </p>
        <div className="flex items-center gap-4 opacity-50">
          <label className="text-sm text-gray-600 w-40">Channel Token</label>
          <input disabled type="text" placeholder="(ยังไม่ได้พัฒนา)"
            className="flex-1 bg-gray-100 text-gray-400 rounded px-3 py-1.5 text-sm border border-gray-200 cursor-not-allowed" />
        </div>
      </Section>
    </PageWrapper>
  )
}
