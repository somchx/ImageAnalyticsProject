import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Monitor, Upload, History, Settings, Flame
} from 'lucide-react'

const links = [
  { to: '/', icon: LayoutDashboard, label: 'แผงควบคุม' },
  { to: '/monitor', icon: Monitor, label: 'ตรวจสอบสด' },
  { to: '/upload', icon: Upload, label: 'อัปโหลด' },
  { to: '/history', icon: History, label: 'ประวัติ' },
  { to: '/settings', icon: Settings, label: 'ตั้งค่า' },
]

export default function Sidebar() {
  return (
    <aside className="w-56 min-h-screen bg-white border-r border-gray-200 flex flex-col">
      <div className="flex items-center gap-2 px-5 py-5 border-b border-gray-200">
        <Flame className="text-orange-500 w-6 h-6" />
        <span className="font-bold text-orange-500 text-lg leading-tight">
          GrillVision
        </span>
      </div>
      <nav className="flex-1 py-4">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-5 py-3 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-orange-50 text-orange-500 border-r-2 border-orange-500'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="px-5 py-3 border-t border-gray-200 text-xs text-gray-400">
        Computer Vision แบบดั้งเดิม · ไม่มี AI/ML
      </div>
    </aside>
  )
}
