# AI Assistant - Ask Kopi Colt 🤠

## Overview

The AI Assistant is an interactive chat interface where users can ask Kopi Colt (your AI trading companion) questions about markets, stocks, portfolio performance, and trading advice.

## Features

### ✅ **Implemented**

1. **Text Input** - Type your questions
2. **Voice Input** - Click 🎤 to speak your question (uses Web Speech API)
3. **Voice Output** - Kopi speaks responses using ElevenLabs TTS
4. **Animated Character** - Kopi's mouth moves when speaking
5. **Two-Part Responses**:
   - **Short Spoken Response** 🗣️ - Quick answer that Kopi reads aloud
   - **Detailed Text Response** 📄 - Full analysis shown in chat (not spoken)
6. **Hardcoded Responses** - Smart responses based on keywords (ready for LLM integration)

### 🎯 **How It Works**

1. User asks a question (text or voice)
2. System analyzes the question and generates response
3. Kopi speaks the short answer (mouth animates)
4. Full detailed analysis appears in chat
5. User can continue the conversation

## Access Points

- **Dashboard**: Click "🤠 Ask Kopi" button in header
- **Home Page**: Click "🤠 Try Kopi Now" in CTA section
- **Direct URL**: `/assistant`

## Supported Questions (Hardcoded Responses)

The system currently recognizes these question types:

### 📈 Stock Queries
- "Should I buy Apple?" / "AAPL"
- "Should I buy DBS?"
- "Tell me about [any bank]"

### 📊 Portfolio Queries
- "How's my portfolio doing?"
- "Show my holdings"
- "Portfolio performance"

### 🌍 Market Queries
- "What's the market outlook?"
- "How's Singapore market?"
- "What's happening today?"
- "Tell me about STI"

### 💰 Crypto Queries
- "Should I buy Bitcoin?"
- "Tell me about crypto"

### ❓ General Questions
- Any other question gets a helpful generic response

## Response Format

### Example Interaction:

**User**: "Should I buy Apple?"

**Kopi (Spoken)** 🗣️:
> "Howdy there Winston! Given the current market conditions, I'mma say hold off on Apple for now, partner."

**Detailed Analysis** 📄 (Not Spoken):
```
Here's why I'm cautious on AAPL right now:

• Valuation Concerns: Trading at 28x P/E, above historical averages
• China Headwinds: iPhone sales in China down 15% YoY
• Margin Pressure: Services growth slowing
• Technical Setup: RSI showing overbought at 72

Better entry would be around $165-170 range.
```

## Technical Details

### Voice Input
- Uses Web Speech API (`webkitSpeechRecognition`)
- Works in Chrome/Edge (Safari limited)
- Click 🎤 to start, speaks automatically when done
- Falls back to text input if not supported

### Voice Output
- Uses ElevenLabs API via `/api/voice/generate`
- "Cowboy" voice profile
- Mouth animation syncs with audio playback
- Auto-stops when user closes or moves to next question

### Character Animation
- **Mouth States**: Closed `—` / Open `O` when speaking
- **Expressions**: 
  - `neutral` - Default state
  - `happy` - Positive responses
  - `concerned` - Warnings/cautions
  - `impressed` - Excited about opportunities
- **Speaking Animation**: Mouth toggles every 150ms while audio plays
- **Body Language**: Slight head bob and hat wiggle when talking

## Integration Points for AI Engineer

### Current Hardcoded Function:
```typescript
const generateHardcodedResponse = (userQuestion: string): { 
  short: string; 
  detailed: string 
}
```

### To Replace With LLM:
```typescript
// Replace this function with:
const generateAIResponse = async (userQuestion: string) => {
  // 1. Call router agent to classify intent
  const intent = await routerAgent.classify(userQuestion)
  
  // 2. Call appropriate specialized agent
  const response = await orchestrator.handle(intent, userQuestion)
  
  // 3. Return structured response
  return {
    short: response.spokenSummary,    // Brief answer for TTS
    detailed: response.fullAnalysis   // Detailed markdown/text
  }
}
```

### API Endpoints Needed:
- `POST /api/ai/chat` - Main chat endpoint
  - Input: `{ message: string, userId: string }`
  - Output: `{ shortResponse: string, detailedResponse: string }`

### RAG Integration:
The detailed response should include:
- Source citations
- Data from Exa.ai searches
- Portfolio context from Supabase
- Risk analysis from MCP tools
- Historical performance data

## Future Enhancements

### Phase 2:
- [ ] Message history persistence (save to Supabase)
- [ ] Rich media in responses (charts, tables)
- [ ] Follow-up question suggestions
- [ ] Export conversation as PDF

### Phase 3:
- [ ] Multi-modal responses (voice + chart annotations)
- [ ] Real-time market data integration
- [ ] Voice-only mode (hands-free trading assistant)
- [ ] Mobile app version with push-to-talk

### Phase 4:
- [ ] Video avatar (lip-synced 3D Kopi)
- [ ] Sentiment analysis of user questions
- [ ] Proactive recommendations based on chat history
- [ ] Multi-language support

## User Experience Notes

### Best Practices:
1. **Voice Input**: Works best in quiet environment
2. **Questions**: Be specific (e.g., "Should I buy DBS?" vs "stocks?")
3. **Patience**: Wait for Kopi to finish speaking before next question
4. **Mobile**: Voice input may not work on all browsers

### Limitations:
- Voice recognition requires Chrome/Edge browser
- Requires microphone permissions
- Voice generation requires internet connection
- Responses are currently hardcoded (demo mode)

## Development Notes

### File Structure:
```
apps/web/app/assistant/
├── page.tsx                          # Main chat interface
└── components/
    └── AnimatedKopiColt.tsx         # Animated character
```

### Key Dependencies:
- `framer-motion` - Character animation
- `Web Speech API` - Voice input
- `ElevenLabs API` - Voice output
- React hooks for audio management

### Testing Voice:
1. Grant microphone permissions
2. Click 🎤 button
3. Speak clearly: "Should I buy DBS?"
4. Wait for transcription to appear
5. Click "Send" or press Enter

---

**Built with 🤠 by the Kopitiam Capital team**

