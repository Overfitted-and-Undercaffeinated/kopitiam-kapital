# Testing Your AI Assistant 🤠

## Quick Start

1. **Start your development server**:
   ```bash
   cd apps/web
   npm run dev
   ```

2. **Navigate to the Assistant**:
   - Go to `http://localhost:3000/assistant`
   - OR click "🤠 Ask Kopi" from the dashboard
   - OR click "🤠 Try Kopi Now" from the home page

---

## Test Scenarios

### 1️⃣ **Text Input Test**

**Steps**:
1. Type in the input field: `Should I buy DBS?`
2. Press Enter or click "Send"
3. Watch Kopi respond!

**Expected**:
- User message appears on right (brown bubble)
- Processing indicator shows briefly
- Kopi's short response appears (gold bubble) 🗣️
- Detailed analysis appears below (gray box) 📄
- Kopi's mouth moves while speaking
- You hear the voice output

---

### 2️⃣ **Voice Input Test** (Chrome/Edge only)

**Steps**:
1. Click the 🎤 button
2. Allow microphone permissions (if prompted)
3. Speak clearly: "How is my portfolio doing?"
4. Wait for transcription to appear
5. Press Enter to send

**Expected**:
- Button turns red and shows "Listening..."
- Your speech gets transcribed to text
- Auto-populates the input field
- Continue as text input

**Note**: If voice doesn't work:
- Check browser compatibility (Chrome/Edge)
- Grant microphone permissions
- Ensure you're on HTTPS (or localhost)
- Try typing instead (always works)

---

### 3️⃣ **Voice Output Test**

**Steps**:
1. Ask any question (text or voice)
2. Wait for response
3. Listen to Kopi speak!

**Expected**:
- "Speaking..." status shows
- Kopi's mouth opens/closes rhythmically
- Hat wiggles slightly
- Speech bubble (💬) appears
- Audio plays from speakers
- Only SHORT response is spoken (not full details)

**Troubleshooting**:
- Check speaker volume
- Ensure browser allows audio playback
- If no sound: detailed text still shows (graceful fallback)

---

### 4️⃣ **Animation Test**

**Steps**:
1. Ask any question
2. Watch Kopi closely while he speaks

**Expected Animations**:
- **Mouth**: Opens → Closes → Opens (repeating)
- **Hat**: Gentle wiggle
- **Head**: Slight bob
- **Badge**: Jiggles
- **Bubble**: 💬 appears beside Kopi
- **Eyes**: Change based on response type

---

### 5️⃣ **Multiple Questions Test**

**Steps**:
1. Ask: `Should I buy Apple?`
2. Wait for full response
3. Ask: `What about DBS?`
4. Ask: `How's the market today?`
5. Ask: `Tell me about my portfolio`

**Expected**:
- Chat history builds up
- Each question gets unique response
- Scroll automatically to latest message
- Previous messages stay visible
- Kopi stops speaking before next response

---

## Suggested Test Questions

### 📈 Stock Questions:
- "Should I buy Apple?"
- "Tell me about DBS"
- "What do you think about Singapore banks?"
- "Should I invest in crypto?"

### 📊 Portfolio Questions:
- "How's my portfolio doing?"
- "Show me my holdings"
- "What's my P&L today?"

### 🌍 Market Questions:
- "What's the market outlook?"
- "How's Singapore market today?"
- "What's happening with STI?"

### ❓ General Questions:
- "What should I do today?"
- "Give me some trading ideas"
- "What stocks should I watch?"

---

## Visual Checklist

When testing, verify these UI elements:

### Header:
- [ ] "Ask Kopi Colt" title
- [ ] "Your AI trading companion" subtitle
- [ ] "Back to Dashboard" button (functional)

### Left Panel (Kopi):
- [ ] Cowboy character visible
- [ ] Hat rendered correctly
- [ ] Mustache visible
- [ ] Sheriff badge shows "AI"
- [ ] Status indicator at bottom

### Right Panel (Chat):
- [ ] Welcome message on load
- [ ] 4 suggestion buttons (clickable)
- [ ] Messages render correctly
- [ ] User messages on right (brown)
- [ ] Kopi messages on left (gold + gray)
- [ ] Auto-scroll to bottom

### Input Area:
- [ ] 🎤 Voice button (left)
- [ ] Text input field (middle)
- [ ] Send button (right)
- [ ] Help text at bottom
- [ ] All disabled during processing

### Status Indicators:
- [ ] 🔴 Listening (red pulsing mic)
- [ ] 🔵 Thinking (blue dot)
- [ ] 🟢 Speaking (green dot)
- [ ] ⚪ Ready (gray dot)

---

## Performance Checks

### Speed:
- [ ] Response < 1 second
- [ ] Voice generation < 2 seconds
- [ ] Smooth animations (60fps)
- [ ] No UI lag

### Reliability:
- [ ] All test questions work
- [ ] No console errors
- [ ] Audio plays every time
- [ ] Animations sync with audio

### Responsiveness:
- [ ] Works on desktop
- [ ] Works on mobile (responsive layout)
- [ ] Input fields scale properly
- [ ] Kopi character scales on small screens

---

## Browser Compatibility Matrix

| Feature | Chrome | Edge | Safari | Firefox |
|---------|--------|------|--------|---------|
| Text Input | ✅ | ✅ | ✅ | ✅ |
| Voice Input | ✅ | ✅ | ⚠️ Limited | ❌ |
| Voice Output | ✅ | ✅ | ✅ | ✅ |
| Animations | ✅ | ✅ | ✅ | ✅ |
| Overall | ✅ | ✅ | ⚠️ | ⚠️ |

---

## Debugging Tips

### No Voice Input?
1. Check browser: Chrome or Edge?
2. Check permissions: Microphone allowed?
3. Check HTTPS: localhost or HTTPS?
4. Fallback: Use text input

### No Voice Output?
1. Check volume: Is sound on?
2. Check API: Is ElevenLabs working?
3. Check console: Any errors?
4. Fallback: Read text response

### Mouth Not Moving?
1. Is audio playing?
2. Check `isSpeaking` state
3. Check console for animation errors
4. Refresh page and try again

### Response Not Showing?
1. Check console for errors
2. Verify `generateHardcodedResponse` function
3. Check message state update
4. Refresh page

---

## Known Issues & Limitations

### Current Limitations:
1. **Responses are hardcoded** - awaiting LLM integration
2. **No conversation memory** - each question is independent
3. **No message persistence** - chat clears on refresh
4. **Voice input Chrome/Edge only** - Web Speech API limitation

### These are Expected:
- Voice input may not work on all browsers → Use text
- First audio playback may need user interaction → Click anywhere first
- Microphone permissions required → Grant when prompted

---

## Next Steps After Testing

### For You (Frontend):
1. ✅ Test all features
2. ✅ Verify animations
3. ✅ Check responsiveness
4. 🔄 Optional: Add message export
5. 🔄 Optional: Add conversation history

### For AI Engineer:
1. Create `/api/ai/chat` endpoint
2. Replace `generateHardcodedResponse()`
3. Integrate Router Agent
4. Add RAG pipeline
5. Add source citations
6. Test end-to-end with real LLM

---

## Success Criteria

Your AI Assistant is working correctly if:

✅ You can type questions and get responses
✅ Voice input transcribes your speech (Chrome/Edge)
✅ Kopi speaks the short response aloud
✅ Detailed analysis appears in text
✅ Kopi's mouth moves while speaking
✅ Animations are smooth and synchronized
✅ Multiple questions work in sequence
✅ Chat history displays correctly
✅ UI is responsive and works on mobile

---

## Demo Script (For Presentation)

**Opening**:
"Let me show you our AI trading assistant, Kopi Colt!"

**Step 1**: Navigate to `/assistant`
"Here's Kopi - your 24/7 trading companion"

**Step 2**: Click 🎤 and ask
"Should I buy DBS?"

**Step 3**: Show response
"Notice how Kopi speaks the recommendation, and provides detailed analysis below"

**Step 4**: Ask follow-up
"What about Apple?" (type this one)

**Step 5**: Show interaction
"The chat interface makes it easy to have a conversation about your trading decisions"

**Closing**:
"Right now responses are templated, but once we connect the LLM backend, Kopi will provide real-time, personalized trading advice based on live market data and your portfolio!"

---

🎉 **You're all set! Go test your AI Assistant now!** 🤠

Navigate to: `http://localhost:3000/assistant`

