'use client'

interface Source {
  title: string
  url: string
  published?: string
}

interface SourceChipsProps {
  sources: Source[]
}

export default function SourceChips({ sources }: SourceChipsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {sources.map((source, idx) => (
        <a
          key={idx}
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 hover:bg-blue-200 transition-colors"
        >
          {source.title}
        </a>
      ))}
    </div>
  )
}

