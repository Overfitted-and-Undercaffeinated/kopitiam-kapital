import { NextRequest, NextResponse } from 'next/server'

// ElevenLabs API configuration
const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY
const VOICE_ID = process.env.KOPI_COLT_VOICE_ID || 'EXAVITQu4vr4xnSDxMaL' // Default: Bella voice (friendly, casual)

export async function POST(request: NextRequest) {
  try {
    const { text, voice } = await request.json()

    if (!text) {
      return NextResponse.json(
        { error: 'Text is required' },
        { status: 400 }
      )
    }

    if (!ELEVENLABS_API_KEY) {
      console.warn('ElevenLabs API key not configured, skipping voice generation')
      return NextResponse.json(
        { error: 'Voice API not configured' },
        { status: 503 }
      )
    }

    // Select voice based on preference
    let selectedVoiceId = VOICE_ID
    if (voice === 'cowboy') {
      // Use a more rugged, masculine voice for Kopi Colt
      selectedVoiceId = process.env.KOPI_COLT_VOICE_ID || 'TxGEqnHWrfWFTfGW9XjX' // Josh - deep, masculine
    }

    // Call ElevenLabs Text-to-Speech API with 2-second timeout
    console.log('⏱️  Starting ElevenLabs API call with 2s timeout...')
    const startTime = Date.now()
    const controller = new AbortController()
    const timeoutId = setTimeout(() => {
      console.log('⏰ Timeout triggered! Aborting ElevenLabs API call...')
      controller.abort()
    }, 2000) // 2 second timeout

    let response
    try {
      response = await fetch(
        `https://api.elevenlabs.io/v1/text-to-speech/${selectedVoiceId}`,
        {
          method: 'POST',
          headers: {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
            'xi-api-key': ELEVENLABS_API_KEY,
          },
          body: JSON.stringify({
            text,
            model_id: 'eleven_monolingual_v1',
            voice_settings: {
              stability: 0.5,
              similarity_boost: 0.75,
              style: 0.5,
              use_speaker_boost: true,
            },
          }),
          signal: controller.signal,
        }
      )
      const elapsed = Date.now() - startTime
      console.log(`✅ ElevenLabs API responded in ${elapsed}ms`)
      clearTimeout(timeoutId)
    } catch (error: any) {
      clearTimeout(timeoutId)
      const elapsed = Date.now() - startTime
      if (error.name === 'AbortError') {
        console.warn(`⏱️  ElevenLabs API timeout after ${elapsed}ms - skipping voice generation`)
        return NextResponse.json(
          { error: 'timeout', message: 'Voice generation timed out, continuing without voice' },
          { status: 408 }
        )
      }
      console.error(`❌ ElevenLabs API error after ${elapsed}ms:`, error.message)
      throw error // Re-throw other errors
    }

    if (!response.ok) {
      const errorText = await response.text()
      console.error('ElevenLabs API error:', errorText)
      
      // Check if it's a quota exceeded or invalid API key error
      let errorData = null
      try {
        errorData = JSON.parse(errorText)
      } catch {}
      
      // Invalid API key - treat as timeout, skip voice generation
      if (errorData?.detail?.status === 'invalid_api_key') {
        console.warn('⚠️  Invalid ElevenLabs API key, skipping voice generation')
        return NextResponse.json(
          { error: 'timeout', message: 'Voice API not configured, continuing without voice' },
          { status: 408 } // Return 408 like a timeout
        )
      }
      
      // Quota exceeded
      if (errorData?.detail?.status === 'quota_exceeded') {
        console.warn('⚠️  ElevenLabs quota exceeded, skipping voice generation')
        return NextResponse.json(
          { error: 'timeout', message: 'Voice API quota exceeded, continuing without voice' },
          { status: 408 } // Return 408 like a timeout
        )
      }
      
      // Other errors - also skip voice
      console.warn('⚠️  ElevenLabs API error, skipping voice generation')
      return NextResponse.json(
        { error: 'timeout', message: 'Voice generation failed, continuing without voice' },
        { status: 408 } // Return 408 like a timeout
      )
    }

    // Return the audio stream
    const audioBuffer = await response.arrayBuffer()
    
    return new NextResponse(audioBuffer, {
      headers: {
        'Content-Type': 'audio/mpeg',
        'Content-Length': audioBuffer.byteLength.toString(),
      },
    })
  } catch (error) {
    console.error('Voice generation error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}


