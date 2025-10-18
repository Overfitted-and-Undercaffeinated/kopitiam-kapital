'use client'

interface AlertToastProps {
  title: string
  message: string
  type: 'info' | 'warning' | 'success' | 'error'
}

export default function AlertToast({ title, message, type }: AlertToastProps) {
  const bgColor = {
    info: 'bg-blue-100 border-blue-500',
    warning: 'bg-yellow-100 border-yellow-500',
    success: 'bg-green-100 border-green-500',
    error: 'bg-red-100 border-red-500',
  }[type]

  return (
    <div className={`border-l-4 p-4 ${bgColor}`}>
      <p className="font-bold">{title}</p>
      <p className="text-sm">{message}</p>
    </div>
  )
}

