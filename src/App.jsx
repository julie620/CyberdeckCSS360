import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [currentPlayback, setPlayback] = useState(null)

  useEffect(() => {
    const fetchPlayback = () => {
      console.log('Fetching playback...')
      fetch('/api/playback', {
        credentials: 'include'
      })
        .then((res) => {
          console.log('Response status:', res.status)
          return res.json()
        })
        .then((data) => {
          console.log('Received data:', data)
          setPlayback(data)
        })
        .catch((error) => {
          console.error('Error fetching playback data:', error)
        })
    }

    fetchPlayback()

    const interval = setInterval(fetchPlayback, 1000)

    return () => clearInterval(interval)
  }, [])

  console.log('Rendering App, currentPlayback:', currentPlayback)

  return (
    <>
      <h1>Spotify Playback</h1>
      {currentPlayback?.auth_required && (
        <a href={currentPlayback.auth_url}>
          Login with Spotify
        </a>
      )}

      {currentPlayback && !currentPlayback.auth_required && (
        <div>
          {currentPlayback.message ? (
            <p>{currentPlayback.message}</p>
          ) : (
            <>
              <p>Currently playing: {currentPlayback.track_name}</p>
              <p>Artist: {currentPlayback.artist_name}</p>
              <p>
                Progress: {
                  Math.floor(currentPlayback.progress_ms / 60000)
                }:
                {
                  String(Math.floor((currentPlayback.progress_ms % 60000) / 1000)).padStart(2, '0')
                }
              </p>
              <p>Status: {currentPlayback.is_playing ? 'Playing' : 'Paused'}</p>
            </>
          )}
        </div>
      )}
    </>
  )
}

export default App
