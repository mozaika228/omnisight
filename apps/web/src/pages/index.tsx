import React from 'react'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-white mb-4">
            OmniSight
          </h1>
          <p className="text-xl text-slate-300 mb-8">
            AI-powered video understanding platform
          </p>
          <div className="space-x-4">
            <button className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition">
              Upload Video
            </button>
            <button className="px-8 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-semibold transition">
              Learn More
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}
