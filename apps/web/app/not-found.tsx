export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h2 className="text-4xl font-bold mb-4">404</h2>
        <p className="text-xl mb-4">Page not found</p>
        <a 
          href="/"
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 inline-block"
        >
          Return Home
        </a>
      </div>
    </div>
  )
}

