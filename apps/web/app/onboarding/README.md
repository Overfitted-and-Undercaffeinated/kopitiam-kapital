# Onboarding Page - Kopi Colt

This directory contains the onboarding experience for Kopitiam Capital, featuring **Kopi Colt**, our 3D polygonal cowboy mascot.

## Features

### Kopi Colt - The Cowboy Mascot
- **3D Low-Poly Model**: Built with Three.js and React Three Fiber
- **Cursor Tracking**: Eyes and head follow your mouse cursor
- **Facial Expressions**: Reacts to user input
  - Neutral: Default state
  - Concerned: When "Aggressive" risk profile selected
  - Impressed: When high trading capital selected
  - Happy: Completing steps and final submission
- **Voice Integration**: Uses ElevenLabs TTS for dialogue
- **Responsive**: Scales and repositions on mobile devices

### 4-Step Onboarding Flow

#### Step 1: Welcome
- Name and email collection
- Kopi Colt intro animation with "Howdy, partner!"

#### Step 2: Risk & Experience
- Risk Profile: Conservative / Moderate / Aggressive
- Experience Level: Beginner / Intermediate / Expert
- Trading Capital Range
- Kopi reacts to risk selection

#### Step 3: Preferences
- Primary Markets (SGX, US, HK)
- Morning Brief delivery time
- Voice preference for audio briefs

#### Step 4: Watchlist
- Add 3-5 stocks to initial watchlist
- Validates ticker symbols
- Final "You're all set, partner!" message

## Setup

### Environment Variables

Add to your `.env.local`:

```bash
ELEVENLABS_API_KEY=your_api_key_here
KOPI_COLT_VOICE_ID=TxGEqnHWrfWFTfGW9XjX  # Josh voice (deep, masculine)
```

### Voice Configuration

The app uses ElevenLabs for voice generation. Available voice IDs:
- `TxGEqnHWrfWFTfGW9XjX` - Josh (default, deep masculine)
- `EXAVITQu4vr4xnSDxMaL` - Bella (friendly, casual)
- `21m00Tcm4TlvDq8ikWAM` - Rachel (clear, professional)

To change Kopi Colt's voice, update `KOPI_COLT_VOICE_ID` in your environment variables.

## Development

Access the onboarding page at:
```
http://localhost:3000/onboarding
```

## Technical Details

### Components
- `page.tsx` - Main onboarding flow with form state management
- `components/KopiColt.tsx` - 3D cowboy character with animations

### Voice API
- Endpoint: `/api/voice/generate`
- Method: POST
- Body: `{ text: string, voice: 'cowboy' }`
- Returns: Audio/MPEG stream

### Animation States
- Intro: Slides up from bottom
- Watching: Positioned in bottom-right corner
- Exit: Slides down on completion

## Future Enhancements
- Additional facial expressions
- Hand gestures and animations
- More voice lines for different interactions
- Customizable cowboy appearance
- Multi-language support


