# AI Assistant - Technical Architecture

## System Flow Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                            │
│                      /assistant page.tsx                          │
└────────────┬─────────────────────────────────┬───────────────────┘
             │                                 │
             │ Voice Input                     │ Text Input
             │                                 │
        ┌────▼────┐                       ┌────▼────┐
        │ 🎤 Web  │                       │ ⌨️ Text  │
        │ Speech  │                       │  Field  │
        │   API   │                       └────┬────┘
        └────┬────┘                            │
             │                                 │
             └──────────┬──────────────────────┘
                        │
                        │ User Question: "Should I buy Apple?"
                        │
                   ┌────▼─────────────────────┐
                   │  handleSendMessage()     │
                   │  - Add user message      │
                   │  - Call response gen     │
                   └────┬─────────────────────┘
                        │
                        │
        ┌───────────────▼──────────────────────────────────┐
        │        generateHardcodedResponse()                │
        │  (TO BE REPLACED WITH LLM + RAG)                 │
        │                                                   │
        │  Input: "Should I buy Apple?"                    │
        │                                                   │
        │  Processing:                                     │
        │  1. Keyword matching                             │
        │  2. Generate structured response                 │
        │                                                   │
        │  Output: {                                       │
        │    short: "Hold off on Apple, partner..."       │
        │    detailed: "• Valuation concerns..."          │
        │  }                                                │
        └───────────────┬──────────────────────────────────┘
                        │
                        │
        ┌───────────────▼──────────────────────────────────┐
        │         Response Rendering                        │
        │                                                   │
        │  1. Add message to chat history                  │
        │  2. Display in UI:                               │
        │     - Short (gold bubble) 🗣️                     │
        │     - Detailed (gray box) 📄                     │
        │                                                   │
        │  3. Trigger voice output ──────┐                 │
        └────────────────────────────────┼─────────────────┘
                                         │
                                         │
                        ┌────────────────▼─────────────────┐
                        │   speakResponse(shortText)       │
                        │                                  │
                        │   POST /api/voice/generate       │
                        │   Body: {                        │
                        │     text: shortText,             │
                        │     voice: 'cowboy'              │
                        │   }                               │
                        └────────────┬─────────────────────┘
                                     │
                                     │
                        ┌────────────▼─────────────────────┐
                        │     ElevenLabs TTS API           │
                        │                                  │
                        │  1. Convert text to speech       │
                        │  2. Return audio blob            │
                        └────────────┬─────────────────────┘
                                     │
                                     │ Audio Blob
                                     │
                        ┌────────────▼─────────────────────┐
                        │    Audio Playback                │
                        │                                  │
                        │  1. Create Audio() element       │
                        │  2. Play audio                   │
                        │  3. Set isSpeaking = true  ──┐   │
                        └──────────────────────────────┼───┘
                                                       │
                                                       │
                        ┌──────────────────────────────▼───┐
                        │   AnimatedKopiColt Component     │
                        │                                  │
                        │  Props:                          │
                        │  - isSpeaking: true              │
                        │  - expression: 'happy'           │
                        │                                  │
                        │  Animation:                      │
                        │  - Mouth opens/closes (150ms)    │
                        │  - Hat wiggles                   │
                        │  - Head bobs                     │
                        │  - Speech bubble shows           │
                        └──────────────────────────────────┘
```

---

## Component Architecture

```
/assistant
│
├── page.tsx (Main Container)
│   │
│   ├── State Management
│   │   ├── messages: Message[]
│   │   ├── inputText: string
│   │   ├── isListening: boolean
│   │   ├── isSpeaking: boolean
│   │   ├── isProcessing: boolean
│   │   └── userName: string
│   │
│   ├── Refs
│   │   ├── audioRef: Audio element
│   │   ├── recognitionRef: SpeechRecognition
│   │   └── messagesEndRef: Auto-scroll
│   │
│   ├── Functions
│   │   ├── startListening()
│   │   ├── stopListening()
│   │   ├── handleSendMessage()
│   │   ├── generateHardcodedResponse()
│   │   └── speakResponse()
│   │
│   └── UI Components
│       ├── Header (title + back button)
│       ├── Grid Layout (2 columns)
│       │   ├── Left: AnimatedKopiColt
│       │   └── Right: Chat Interface
│       │       ├── Messages Area
│       │       │   ├── Welcome prompt
│       │       │   ├── Message bubbles
│       │       │   └── Auto-scroll
│       │       └── Input Area
│       │           ├── Voice button (🎤)
│       │           ├── Text input
│       │           └── Send button
│       └── Status Indicator
│
└── components/
    │
    └── AnimatedKopiColt.tsx
        │
        ├── Props
        │   ├── isSpeaking: boolean
        │   └── expression: string
        │
        ├── State
        │   └── mouthOpen: boolean (toggles while speaking)
        │
        ├── Effects
        │   └── Mouth animation interval (150ms)
        │
        └── SVG Elements
            ├── Hat (with brim & crown)
            ├── Face (head ellipse)
            ├── Eyes (expression-based)
            ├── Nose
            ├── Mouth (animated when speaking)
            ├── Mustache
            ├── Bandana/Neckerchief
            ├── Vest & Shirt
            ├── Sheriff Badge ("AI" text)
            └── Speech Bubble (shows when speaking)
```

---

## Data Flow

### Message Structure
```typescript
interface Message {
  id: string                    // Timestamp-based ID
  role: 'user' | 'assistant'    // Who sent it
  userMessage?: string          // User's question
  shortResponse?: string        // Kopi's spoken answer
  detailedResponse?: string     // Full text analysis
  timestamp: Date               // When sent
}
```

### Response Generation Flow
```typescript
// 1. User sends message
const userMsg: Message = {
  id: Date.now().toString(),
  role: 'user',
  userMessage: "Should I buy Apple?",
  timestamp: new Date()
}

// 2. Generate AI response (currently hardcoded)
const { short, detailed } = generateHardcodedResponse(userMsg.userMessage)

// 3. Create assistant message
const assistantMsg: Message = {
  id: (Date.now() + 1).toString(),
  role: 'assistant',
  shortResponse: short,      // "Howdy there! I'd say no..."
  detailedResponse: detailed, // "• Valuation concerns..."
  timestamp: new Date()
}

// 4. Speak the short response
await speakResponse(short)
```

---

## Voice Integration

### Input Pipeline
```javascript
// Initialize Web Speech API
const SpeechRecognition = window.webkitSpeechRecognition
const recognition = new SpeechRecognition()

recognition.continuous = false    // One utterance at a time
recognition.interimResults = false // Final results only
recognition.lang = 'en-US'         // English

// Handle results
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript
  setInputText(transcript)  // Auto-populate input field
}

// Handle errors
recognition.onerror = (event) => {
  console.error('Speech error:', event.error)
  setIsListening(false)
}
```

### Output Pipeline
```javascript
// Generate voice from text
const speakResponse = async (text: string) => {
  // 1. Call ElevenLabs API
  const response = await fetch('/api/voice/generate', {
    method: 'POST',
    body: JSON.stringify({ 
      text,           // Short response only
      voice: 'cowboy' // Voice profile
    })
  })

  // 2. Get audio blob
  const audioBlob = await response.blob()
  const audioUrl = URL.createObjectURL(audioBlob)

  // 3. Create and play audio
  const audio = new Audio(audioUrl)
  audioRef.current = audio

  // 4. Set speaking state (triggers animation)
  setIsSpeaking(true)

  // 5. Handle playback end
  audio.onended = () => {
    setIsSpeaking(false)    // Stop mouth animation
    URL.revokeObjectURL(audioUrl) // Clean up
  }

  await audio.play()
}
```

---

## Animation Synchronization

### Mouth Movement Logic
```typescript
// In AnimatedKopiColt component
useEffect(() => {
  if (!isSpeaking) {
    setMouthOpen(false)
    return
  }

  // Toggle mouth every 150ms while speaking
  const interval = setInterval(() => {
    setMouthOpen(prev => !prev)  // Toggle open/closed
  }, 150)

  return () => clearInterval(interval)
}, [isSpeaking])

// Render mouth based on state
const getMouthShape = () => {
  if (isSpeaking && mouthOpen) return 'O'  // Open
  if (isSpeaking && !mouthOpen) return '—' // Closed
  // ... expression-based shapes
}
```

### Expression System
```typescript
type Expression = 'neutral' | 'happy' | 'concerned' | 'impressed'

const getEyeExpression = (expr: Expression) => {
  switch (expr) {
    case 'happy': return '◡◡'      // Smile eyes
    case 'concerned': return '︵︵'  // Worried
    case 'impressed': return '◉◉'  // Wide
    default: return '••'            // Neutral
  }
}
```

---

## State Management Flow

```
┌─────────────────────────────────────────────────┐
│           Component State                        │
├─────────────────────────────────────────────────┤
│                                                  │
│  messages: Message[]                             │
│  ├─ User message                                 │
│  ├─ Assistant response (short + detailed)       │
│  └─ Timestamp                                    │
│                                                  │
│  inputText: string                               │
│  └─ Controlled input field                      │
│                                                  │
│  isListening: boolean                            │
│  ├─ Controls mic button state                   │
│  └─ Shows "Listening..." indicator              │
│                                                  │
│  isSpeaking: boolean  ◄─────┐                   │
│  ├─ Triggers mouth animation │                   │
│  ├─ Disables input           │                   │
│  └─ Shows "Speaking..." status                   │
│                              │                   │
│  isProcessing: boolean       │                   │
│  ├─ Disables input           │                   │
│  └─ Shows "Thinking..." status                   │
│                              │                   │
│  audioRef: Audio             │                   │
│  └─ Controls playback ───────┘                   │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## Integration Points for Backend

### Current (Hardcoded):
```typescript
// Line 138 in page.tsx
const generateHardcodedResponse = (userQuestion: string) => {
  // Keyword matching logic
  if (question.includes('apple')) {
    return { short: "...", detailed: "..." }
  }
  // ... more patterns
}
```

### Target (LLM Integration):
```typescript
const generateAIResponse = async (userQuestion: string) => {
  // 1. Call AI backend
  const response = await fetch('/api/ai/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: userQuestion,
      userId: localStorage.getItem('userId'),
      conversationId: currentConversationId
    })
  })

  const data = await response.json()

  // 2. Return structured response
  return {
    short: data.spokenSummary,    // Brief for TTS
    detailed: data.fullAnalysis   // Full markdown
  }
}

// Backend should return:
{
  spokenSummary: "Howdy! I'd say buy DBS, partner!",
  fullAnalysis: "## Bull Case for DBS\n\n• Strong earnings...",
  sources: [
    { title: "DBS Q3 Results", url: "...", type: "news" }
  ],
  confidence: 0.85,
  intent: "RECOMMEND",
  entities: ["DBS"]
}
```

---

## API Contracts

### `/api/voice/generate` (Already Exists)
```typescript
// Request
POST /api/voice/generate
{
  text: string,        // Text to convert to speech
  voice: 'cowboy'      // Voice profile
}

// Response
Audio Blob (MP3/WAV)
```

### `/api/ai/chat` (To Be Created by AI Engineer)
```typescript
// Request
POST /api/ai/chat
{
  message: string,            // User's question
  userId: string,             // From localStorage
  conversationId?: string,    // For context
  includePortfolio?: boolean, // Include user portfolio data
  includeMarket?: boolean     // Include market context
}

// Response
{
  spokenSummary: string,      // Short answer for TTS (max 2-3 sentences)
  fullAnalysis: string,       // Detailed markdown text
  sources?: Array<{           // RAG citations
    title: string,
    url: string,
    type: 'news' | 'research' | 'data',
    relevance: number
  }>,
  confidence: number,         // 0-1
  intent: string,             // Router classification
  entities: string[],         // Extracted tickers/terms
  conversationId: string      // For follow-ups
}
```

---

## Performance Considerations

### Audio Management
- ✅ Clean up audio blobs after playback
- ✅ Stop previous audio before new playback
- ✅ Revoke object URLs to prevent memory leaks
- ✅ Handle errors gracefully

### State Updates
- ✅ Debounce voice input
- ✅ Prevent double-sends
- ✅ Disable inputs while processing
- ✅ Auto-scroll to latest message

### Animation
- ✅ Use CSS/Framer Motion (GPU accelerated)
- ✅ Cleanup intervals on unmount
- ✅ Conditional rendering for performance

---

## Error Handling

```typescript
// Voice Input Errors
recognition.onerror = (event) => {
  switch (event.error) {
    case 'no-speech':
      // User didn't speak - just stop
      break
    case 'audio-capture':
      alert('Microphone not available')
      break
    case 'not-allowed':
      alert('Microphone permission denied')
      break
    default:
      console.error('Speech error:', event.error)
  }
  setIsListening(false)
}

// Voice Output Errors
audio.onerror = () => {
  console.error('Audio playback failed')
  setIsSpeaking(false)
  // Fallback: user can still read text response
}

// API Errors
try {
  const response = await fetch('/api/voice/generate', {...})
  if (!response.ok) {
    throw new Error('Voice generation failed')
  }
} catch (error) {
  console.error('Voice API error:', error)
  setIsSpeaking(false)
  // Text response still shows - graceful degradation
}
```

---

**Ready for LLM integration! Just replace the response generation function and hook up your AI backend! 🚀**

