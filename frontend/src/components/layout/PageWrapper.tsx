import { ReactNode } from 'react'

interface Props {
  title: string
  children: ReactNode
  action?: ReactNode
}

export default function PageWrapper({ title, children, action }: Props) {
  return (
    <div className="flex-1 flex flex-col overflow-auto bg-gray-50">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-white">
        <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
        {action}
      </div>
      <div className="flex-1 p-6">{children}</div>
    </div>
  )
}
