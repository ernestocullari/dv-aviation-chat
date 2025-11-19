# DV Aviation AI Chat Agent - L7 Pilot Deployment

**Status**: Ready to Deploy ✅
**Deployment Time**: 15 minutes
**Business**: DV Aviation (Private Aviation Services)
**Location**: Midland, TX

---

## 📦 What's Included

This is a **minimal L7 implementation** - just what's needed to validate the product:

✅ **FastAPI Backend** (`app/main.py` - 230 lines)
- SSE streaming chat with Claude 3.5 Haiku
- Knowledge base integration (DV Aviation services)
- Health checks and CORS
- Professional system prompts

✅ **Knowledge Base** (`knowledge/context.json`)
- DV Aviation services (Charter, Management, Maintenance, etc.)
- Contact information and locations
- FAQs (10 common questions)
- Core values (Safety, Transparency, Control)

✅ **Deployment Files**
- `Dockerfile` - Optimized for Cloud Run
- `requirements.txt` - Minimal dependencies
- `deploy.sh` - One-command deployment

✅ **Business Documents**
- `PILOT_PROPOSAL.md` - Complete proposal for DV Aviation
- Pricing: $0 pilot, $290/month after

❌ **NOT Included** (L7 principle - validate first, then build):
- No voice integration (text chat validation first)
- No multi-model routing (Haiku for speed/cost)
- No session persistence (measure value first)
- No analytics dashboard (manual tracking for pilot)

---

## 🚀 Quick Deploy (15 Minutes)

### Prerequisites

```bash
# Check you have these:
- Google Cloud account with billing enabled
- gcloud CLI installed
- Anthropic API key

# If missing gcloud:
# https://cloud.google.com/sdk/docs/install
```

### Step 1: Set Environment Variables (1 minute)

```bash
# Navigate to project
cd /tmp/dv-aviation-chat/

# Set your Anthropic API key
export ANTHROPIC_API_KEY='your-anthropic-key-here'

# Optional: Set GCP project (defaults to n8n-agent-451019)
export GCP_PROJECT_ID='your-project-id'
```

### Step 2: Deploy to Cloud Run (10 minutes)

```bash
# Run deployment script
./deploy.sh

# This will:
# 1. Create secret for API key
# 2. Build Docker image
# 3. Deploy to Cloud Run (us-east4)
# 4. Output service URL

# Expected output:
# ========================================
# ✅ Deployment Complete!
# ========================================
# Service URL: https://dv-aviation-chat-xyz.run.app
```

### Step 3: Test Deployment (2 minutes)

```bash
# Health check
curl https://dv-aviation-chat-xyz.run.app/health

# Expected:
# {"status":"healthy","service":"dv-aviation-chat","knowledge_base":"loaded"}

# Test chat (non-streaming)
curl -X POST https://dv-aviation-chat-xyz.run.app/api/chat/message \
  -H 'Content-Type: application/json' \
  -d '{"message": "What charter services do you offer?"}'

# Expected: JSON response with aviation services info

# Test chat (streaming)
curl -N https://dv-aviation-chat-xyz.run.app/api/chat/message/stream \
  -H 'Content-Type: application/json' \
  -d '{"message": "How do I book a flight?"}'

# Expected: SSE stream with typewriter-style response
```

### Step 4: Embed on Website (2 minutes)

Add to dvaviation.com footer (before `</body>`):

```html
<!-- DV Aviation AI Chat Agent -->
<script src="https://dv-aviation-chat-xyz.run.app/shared/universal-chat-widget.js"></script>
<script>
  new UniversalChatWidget({
    apiUrl: 'https://dv-aviation-chat-xyz.run.app',
    primaryColor: '#1E3A8A',  // Aviation blue
    secondaryColor: '#2C3E50',
    companyName: 'DV Aviation',
    enableVoice: false,  // Text only for pilot
    welcomeMessage: 'Hello! I\'m the DV Aviation AI assistant. How can I help you today?'
  });
</script>
```

**Done!** Chat widget now appears on dvaviation.com.

---

## 🧪 Testing Checklist

### Browser Testing

1. **Open dvaviation.com**
   - [ ] Chat button appears in bottom-right
   - [ ] Button shows "DV Aviation"
   - [ ] Button uses aviation blue color

2. **Click Chat Button**
   - [ ] Widget opens smoothly
   - [ ] Welcome message displays
   - [ ] Input field is focused

3. **Test Questions**
   - [ ] "What charter services do you offer?"
     - Should explain flexibility, luxury, customization
   - [ ] "How much does a charter flight cost?"
     - Should mention varies by needs, direct to call 432-561-9111
   - [ ] "What are your hours?"
     - Should provide contact info (24/7 inquiry response)
   - [ ] "Where are you located?"
     - Should give Midland, TX address
   - [ ] "How do you ensure safety?"
     - Should emphasize safety commitment, OEM-trained techs
   - [ ] "Can you help me buy an aircraft?"
     - Should describe acquisition services

4. **Response Quality**
   - [ ] Responses stream with typewriter effect
   - [ ] Formatting looks professional
   - [ ] Tone is professional and aviation-appropriate
   - [ ] Responses reference Safety/Transparency/Control when relevant

5. **Mobile Testing**
   - [ ] Open on iPhone/iPad
   - [ ] Widget is responsive
   - [ ] Chat works smoothly
   - [ ] No layout issues

### API Testing

```bash
SERVICE_URL="https://dv-aviation-chat-xyz.run.app"

# Test 1: Health check
curl $SERVICE_URL/health | jq

# Test 2: Charter inquiry
curl -X POST $SERVICE_URL/api/chat/message \
  -H 'Content-Type: application/json' \
  -d '{"message": "I need to charter a jet for a business trip"}' | jq

# Test 3: Pricing question
curl -X POST $SERVICE_URL/api/chat/message \
  -H 'Content-Type: application/json' \
  -d '{"message": "How much will it cost?"}' | jq

# Test 4: Safety question
curl -X POST $SERVICE_URL/api/chat/message \
  -H 'Content-Type: application/json' \
  -d '{"message": "How do you ensure my safety?"}' | jq

# Test 5: Maintenance inquiry
curl -X POST $SERVICE_URL/api/chat/message \
  -H 'Content-Type: application/json' \
  -d '{"message": "Do you offer maintenance services?"}' | jq
```

---

## 📊 Measuring Success (30-Day Pilot)

### Week 1: Deployment & Baseline

Track manually:
- [ ] Deployment completed successfully
- [ ] Widget live on dvaviation.com
- [ ] First conversation recorded
- [ ] Team trained on monitoring

**Key Metrics**:
- Deployment time: _____ minutes (target: 15 min)
- First response quality: ___/10
- Website visitors: _____ per day
- Chat engagements: _____

### Week 2-3: Active Monitoring

Check Cloud Run logs daily:

```bash
# View recent conversations
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=dv-aviation-chat \
  AND jsonPayload.message=~'Chat request'" \
  --limit 20 --format=json
```

Track:
- [ ] Total conversations: _____
- [ ] Common questions (categorize)
- [ ] Successful responses: _____%
- [ ] Escalations to phone: _____
- [ ] After-hours inquiries: _____

**Questions to Answer**:
1. What are the top 5 questions asked?
2. Is AI answering correctly? (read sample conversations)
3. Are customers finding it helpful? (feedback?)
4. Are routine phone calls reducing? (ask staff)
5. Any knowledge gaps? (questions AI can't answer)

### Week 4: Results Review

Calculate ROI:
- **Time Saved**: Chat conversations × 5 min avg phone call = _____ hours
- **Hours × $50/hr staff cost** = $_____/month saved
- **After-hours leads**: _____ (high value - they might have gone elsewhere)
- **Customer satisfaction**: _____/10 (survey sample customers)

**Decision Point**:
- [ ] Continue at $290/month (ROI positive)
- [ ] Request customization (needs improvements)
- [ ] Cancel (not seeing value)

---

## 🔧 Customization (If Needed)

### Update Knowledge Base

Edit `/tmp/dv-aviation-chat/knowledge/context.json`:

```json
{
  "faqs": [
    {
      "category": "New Category",
      "question": "New question?",
      "answer": "New answer with specifics",
      "keywords": ["search", "terms"]
    }
  ]
}
```

Redeploy:
```bash
./deploy.sh  # Updates with new knowledge
```

### Adjust AI Tone

Edit `app/main.py`, function `build_system_prompt()`:

```python
# Line ~180
"Be professional yet approachable"  # Change to:
"Be highly technical and detailed"  # or whatever tone you want
```

### Add Features Later

**Voice Integration** (+$25/month):
- See `/tmp/unified-ai-chat-template/` for voice code
- Requires ElevenLabs API key
- Add 2-3 hours development

**Analytics Dashboard**:
- See `/tmp/unified-ai-chat-template/infrastructure/business-intelligence/`
- Tracks usage, ROI, health scores
- Add 1-2 hours setup

**Multi-Model Routing** (60% cost savings):
- Routes simple queries to Haiku, complex to Sonnet
- Add 1 hour development
- Saves ~$150/month at scale

---

## 💰 Costs Breakdown

### During Pilot (30 Days)

**Your Costs**:
- Setup: $0 (waived)
- Monthly: $0 (free trial)
- **Total**: **$0**

**Our Costs** (we eat for pilot):
- AI API (Claude): ~$40
- Cloud Run: ~$15
- Support: ~$25
- **Total**: ~$80

### After Pilot (If Continue)

**Monthly Fee**: $290

**Actual Costs**:
| Item | Cost | Notes |
|------|------|-------|
| Claude API | $40 | ~1,000 conversations/month |
| Cloud Run | $15 | Always-on, auto-scaling |
| Infrastructure | $10 | Monitoring, logs |
| Support | $25 | Updates, fixes, questions |
| **Subtotal** | **$90** | |
| Our margin | $200 | 30+ hours/month work |
| **Total** | **$290** | |

**Your ROI**:
- Staff time saved: 5-10 hrs/month = $250-500
- After-hours leads: 2-5/month = $10,000-50,000 potential
- Customer satisfaction: Priceless

**Break-even**: Capture 1 charter booking every 2-3 months.

---

## 📞 Support

### During Pilot

- **Response time**: Same day for issues
- **Contact**: [Your email/phone]
- **Availability**: Mon-Fri 9am-6pm, on-call for critical issues

### Common Issues

**Chat not appearing?**
```bash
# Check widget script is in page source
view-source:https://dvaviation.com
# Search for "universal-chat-widget.js"
```

**Responses not relevant?**
- Check logs for what questions are being asked
- We'll update knowledge base within 24 hours

**Errors in responses?**
```bash
# Check logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=dv-aviation-chat \
  AND severity>=ERROR" --limit 10
```

---

## 🎯 Next Steps

### Option 1: Deploy Now (Recommended)

```bash
cd /tmp/dv-aviation-chat/
export ANTHROPIC_API_KEY='your-key'
./deploy.sh
# 15 minutes later: Live chat on dvaviation.com
```

### Option 2: Local Testing First

```bash
cd /tmp/dv-aviation-chat/
pip install -r requirements.txt
export ANTHROPIC_API_KEY='your-key'
python -m app.main
# Open http://localhost:8080
# Test before deploying
```

### Option 3: Review Proposal

- Send `PILOT_PROPOSAL.md` to DV Aviation
- Schedule demo call
- Deploy after approval

---

## 📚 Documentation

- **This file**: Deployment guide
- **PILOT_PROPOSAL.md**: Business proposal for DV Aviation
- **app/main.py**: Backend code (well-commented)
- **knowledge/context.json**: AI knowledge base
- **deploy.sh**: Deployment script

For universal template and advanced features:
- `/tmp/unified-ai-chat-template/` - Full-featured template
- Includes voice, analytics, automation, BI

---

## ✅ Deployment Checklist

Before deploying:
- [ ] ANTHROPIC_API_KEY environment variable set
- [ ] GCP project configured
- [ ] Reviewed knowledge base for accuracy
- [ ] Tested locally (optional but recommended)

During deployment:
- [ ] Run `./deploy.sh`
- [ ] Health check passes
- [ ] Test chat endpoint
- [ ] Embed widget on website

After deployment:
- [ ] Browser test (desktop + mobile)
- [ ] Sample conversation quality check
- [ ] Share with DV Aviation team
- [ ] Schedule 1-week check-in

30-day pilot:
- [ ] Weekly monitoring
- [ ] Knowledge base updates as needed
- [ ] Results review (week 4)
- [ ] Go/no-go decision

---

**Ready to deploy? Run `./deploy.sh` and you're live in 15 minutes!** ✈️
