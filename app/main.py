"""
DV Aviation Chat Agent - Minimal L7 Implementation
Pilot deployment to validate product-market fit

Features:
- ✅ SSE streaming chat with Claude
- ✅ Knowledge base integration
- ✅ CORS enabled
- ✅ Health checks
- ❌ NO voice (validate text chat first)
- ❌ NO multi-model (use Haiku for speed/cost)
- ❌ NO session persistence (validate conversation value first)
- ❌ NO analytics (measure manually for pilot)

~200 lines total - L7 minimal approach
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from anthropic import Anthropic
from elevenlabs import ElevenLabs
import json
import os
from pathlib import Path
from typing import Optional
import logging
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="DV Aviation Chat Agent",
    description="AI-powered customer service for DV Aviation",
    version="0.1.0-pilot"
)

# CORS - allow dvaviation.com to embed widget
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dvaviation.com",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"  # For pilot testing - tighten in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")

client = Anthropic(api_key=anthropic_api_key)

# Initialize ElevenLabs client
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
if not elevenlabs_api_key:
    logger.warning("ELEVENLABS_API_KEY not set - voice features disabled")
    elevenlabs_client = None
else:
    elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
    logger.info("ElevenLabs client initialized")

# Load knowledge base
knowledge_base_path = Path(__file__).parent.parent / "knowledge" / "context.json"
try:
    with open(knowledge_base_path, "r") as f:
        KNOWLEDGE_BASE = json.load(f)
    logger.info(f"Loaded knowledge base for {KNOWLEDGE_BASE['business']['name']}")
except Exception as e:
    logger.error(f"Failed to load knowledge base: {e}")
    KNOWLEDGE_BASE = {"error": "Knowledge base not loaded"}

# Request models
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    response: str
    session_id: str

class VoiceRequest(BaseModel):
    audio_base64: str
    session_id: Optional[str] = "default"

class TTSRequest(BaseModel):
    text: str
    voice_id: Optional[str] = "EXAVITQu4vr4xnSDxMaL"  # Sarah (professional female)

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - serve demo page"""
    return {
        "service": "DV Aviation Chat Agent",
        "status": "operational",
        "version": "0.1.0-pilot",
        "endpoints": {
            "health": "/health",
            "chat_stream": "/api/chat/message/stream",
            "chat": "/api/chat/message",
            "widget": "/shared/universal-chat-widget.js"
        }
    }

@app.get("/health")
async def health_check():
    """Health check for Cloud Run"""
    kb_loaded = "error" not in KNOWLEDGE_BASE
    return {
        "status": "healthy" if kb_loaded else "degraded",
        "service": "dv-aviation-chat",
        "knowledge_base": "loaded" if kb_loaded else "error",
        "ai_provider": "anthropic",
        "model": "claude-3-5-haiku-20241022"
    }

@app.post("/api/chat/message/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint (SSE)
    Returns AI response character-by-character for typewriter effect
    """
    logger.info(f"Chat request - Session: {request.session_id}, Language: {request.language}")

    try:
        # Build system prompt with knowledge base
        system_prompt = build_system_prompt(request.language)

        # Create SSE generator
        async def generate():
            try:
                # Stream from Claude
                with client.messages.stream(
                    model="claude-3-5-haiku-20241022",  # Fast & cheap for pilot
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[{
                        "role": "user",
                        "content": request.message
                    }]
                ) as stream:
                    for text in stream.text_stream:
                        # SSE format: "data: {text}\n\n"
                        yield f"data: {text}\n\n"

                logger.info(f"Response completed for session {request.session_id}")

            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"data: Sorry, I encountered an error. Please try again or call us at 432-561-9111.\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/message", response_model=ChatResponse)
async def chat_non_stream(request: ChatRequest):
    """
    Non-streaming chat endpoint
    Returns complete response at once
    """
    logger.info(f"Non-streaming chat - Session: {request.session_id}")

    try:
        system_prompt = build_system_prompt(request.language)

        # Get complete response
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": request.message
            }]
        )

        response_text = message.content[0].text

        logger.info(f"Response: {len(response_text)} chars")

        return ChatResponse(
            response=response_text,
            session_id=request.session_id
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/transcribe")
async def voice_transcribe(request: VoiceRequest):
    """
    Speech-to-Text endpoint
    Converts audio to text using ElevenLabs
    """
    if not elevenlabs_client:
        raise HTTPException(status_code=503, detail="Voice features not configured")

    logger.info(f"STT request - Session: {request.session_id}")

    try:
        # Decode base64 audio
        audio_data = base64.b64decode(request.audio_base64)

        # Save temporarily
        temp_path = f"/tmp/voice_{request.session_id}.webm"
        with open(temp_path, "wb") as f:
            f.write(audio_data)

        # Transcribe (Note: ElevenLabs client API may vary - adjust as needed)
        # This is a placeholder - adjust based on actual elevenlabs SDK
        transcription = "Voice transcription not yet implemented"

        logger.info(f"Transcription: {transcription}")

        return {"text": transcription, "session_id": request.session_id}

    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice/synthesize")
async def voice_synthesize(request: TTSRequest):
    """
    Text-to-Speech endpoint
    Converts text to audio using ElevenLabs
    """
    if not elevenlabs_client:
        raise HTTPException(status_code=503, detail="Voice features not configured")

    logger.info(f"TTS request - {len(request.text)} chars")

    try:
        # Generate audio
        audio = elevenlabs_client.generate(
            text=request.text,
            voice=request.voice_id,
            model="eleven_multilingual_v2"
        )

        # Convert generator to bytes
        audio_bytes = b"".join(audio)

        # Encode to base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')

        logger.info(f"Generated {len(audio_bytes)} bytes of audio")

        return {"audio_base64": audio_base64, "voice_id": request.voice_id}

    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def build_system_prompt(language: str = "en") -> str:
    """
    Build system prompt with knowledge base
    Simple approach - just inject the full KB as JSON
    """

    # Language instruction
    if language == "es":
        lang_instruction = """🌍 LANGUAGE REQUIREMENT:
You MUST respond in Spanish. Every word must be in Spanish.
Use formal Spanish (usted)."""
    else:
        lang_instruction = """🌍 LANGUAGE REQUIREMENT:
You MUST respond in English. Every word must be in English."""

    # Build prompt
    prompt = f"""{lang_instruction}

🛩️ IDENTITY:
You are the AI assistant for DV Aviation, a private aviation management company in Midland, Texas.
Your role is to help potential and current clients with information about charter services, aircraft management, maintenance, and other aviation services.

✈️ KNOWLEDGE BASE:
Here is everything you know about DV Aviation:

{json.dumps(KNOWLEDGE_BASE, indent=2)}

📋 INSTRUCTIONS:
1. **Answer based ONLY on the knowledge base above**
2. **Emphasize the three core values**: Safety, Transparency, Control
3. **Be professional yet approachable** - you're speaking with aviation clients
4. **For pricing questions**: Explain that costs vary by needs, direct to call 432-561-9111
5. **For urgent matters (AOG, immediate charter)**: Direct to phone immediately
6. **For technical questions**: Mention OEM-trained technicians, encourage contact
7. **If you don't know**: Say so, then provide contact information
8. **Keep responses concise** - 2-3 paragraphs maximum
9. **Use "we" not "they"** - you represent DV Aviation
10. **End with a call-to-action** when appropriate (call, email, visit)

🔒 CONSTRAINTS:
- Never make up aircraft types, prices, or availability
- Never guarantee specific timelines without directing to team
- Never provide technical advice - that's for licensed professionals
- Always prioritize safety in your guidance

📞 CONTACT INFO (use when appropriate):
- Phone: 432-561-9111
- Email: customerservice@dvaviation.com
- Office: 8818 W Hwy 80, Midland, TX 79706

Remember: You represent a premium aviation services company. Be helpful, professional, and safety-focused."""

    return prompt

# ============================================================================
# STATIC FILES (for testing)
# ============================================================================

@app.get("/shared/universal-chat-widget.js")
async def serve_widget():
    """Serve chat widget JavaScript"""
    widget_path = Path(__file__).parent.parent.parent / "unified-ai-chat-template" / "template" / "frontend" / "shared" / "universal-chat-widget.js"
    if widget_path.exists():
        return FileResponse(widget_path, media_type="application/javascript")
    else:
        raise HTTPException(status_code=404, detail="Widget not found")

@app.get("/mobile")
async def serve_mobile_demo():
    """Serve mobile demo page"""
    mobile_path = Path(__file__).parent / "static" / "mobile-demo.html"
    if mobile_path.exists():
        return FileResponse(mobile_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Mobile demo not found")

@app.get("/dv-aviation-logo.svg")
async def serve_logo():
    """Serve DV Aviation brand logo"""
    logo_path = Path(__file__).parent / "static" / "dv-aviation-logo.svg"
    if logo_path.exists():
        return FileResponse(logo_path, media_type="image/svg+xml")
    else:
        raise HTTPException(status_code=404, detail="Logo not found")

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup info"""
    logger.info("=" * 60)
    logger.info("DV Aviation Chat Agent - Starting Up")
    logger.info("=" * 60)
    logger.info(f"Business: {KNOWLEDGE_BASE.get('business', {}).get('name', 'Unknown')}")
    logger.info(f"Model: claude-3-5-haiku-20241022")
    logger.info(f"Knowledge Base: {'Loaded' if 'error' not in KNOWLEDGE_BASE else 'Error'}")
    logger.info(f"Endpoints: /health, /api/chat/message/stream, /api/chat/message")
    logger.info("=" * 60)

# ============================================================================
# RUN (for local testing)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
