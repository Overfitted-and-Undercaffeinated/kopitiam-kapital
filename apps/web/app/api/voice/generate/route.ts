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

    // Call ElevenLabs Text-to-Speech API
    const response = await fetch(
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
      }
    )

    if (!response.ok) {
      const error = await response.text()
      console.error('ElevenLabs API error:', error)
      return NextResponse.json(
        { error: 'Failed to generate voice' },
        { status: response.status }
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


