'use client'

import { useState } from 'react'

interface AudioPlayerProps {
  url: string
  title?: string
}

export default function AudioPlayer({ url, title }: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)

  return (
    <div className="bg-gray-100 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-semibold text-gray-700">
            {title || 'Audio Briefing'}
          </p>
        </div>
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          {isPlaying ? 'Pause' : 'Play'}
        </button>
      </div>
      <audio src={url} controls className="w-full mt-2" />
    </div>
  )
}

