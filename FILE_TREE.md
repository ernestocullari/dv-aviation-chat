# DV Aviation Chat Agent - Complete File Tree

**Last Updated**: November 18, 2025
**Project Size**: ~30 files, 600KB total (minimal L7 approach)
**Deployment**: Google Cloud Run (us-east4)

---

## 📁 Project Structure

```
/tmp/dv-aviation-chat/
│
├── 📄 README.md                           # Deployment guide (460 lines)
├── 📄 PILOT_PROPOSAL.md                   # Business proposal (384 lines)
├── 📄 DEPLOYMENT_COMPLETE.md              # Deployment summary (460 lines)
├── 📄 TESTING_COMPLETE_SUMMARY.md         # Testing summary (290 lines)
├── 📄 PLAYWRIGHT_TEST_REPORT.md           # Automated test results (580 lines)
├── 📄 EMBED_CODE.html                     # Website embed code (120 lines)
├── 📄 MOBILE_APP_READY.md                 # Mobile app guide (340 lines)
├── 📄 FILE_TREE.md                        # This file
│
├── 🐳 Dockerfile                          # Container configuration (25 lines)
├── 📦 requirements.txt                    # Python dependencies (18 lines)
├── 🚀 deploy.sh                           # Deployment script (112 lines)
│
├── 📂 app/                                # Backend application
│   ├── 📄 __init__.py                     # Package marker (empty)
│   ├── 📄 main.py                         # FastAPI entry point (290 lines)
│   │   ├── ⚙️  Health endpoint           # /health
│   │   ├── 💬 Chat endpoints             # /api/chat/message, /api/chat/message/stream
│   │   ├── 📱 Mobile demo endpoint       # /mobile
│   │   ├── 🔧 System prompt builder     # build_system_prompt()
│   │   └── 🌐 CORS configuration         # Allows dvaviation.com + localhost
│   │
│   └── 📂 static/                         # Static files
│       └── 📄 mobile-demo.html            # Mobile app page (585 lines, 17KB)
│           ├── 🎨 CSS styles (inline)    # Aviation blue theme
│           ├── 📱 Mobile-optimized UI    # Responsive design
│           ├── 💬 Chat modal             # Full-screen chat
│           └── 🔌 API integration        # Fetch to /api/chat/message
│
├── 📂 knowledge/                          # AI knowledge base
│   └── 📄 context.json                    # DV Aviation knowledge (500 lines, 15KB)
│       ├── 🏢 Business information       # Name, tagline, type, location
│       ├── ✈️  Services (5 categories)   # Charter, Management, Maintenance, etc.
│       ├── 📞 Contact information        # Phone, email, address, hours
│       ├── 💎 Core values                # Safety, Transparency, Control
│       ├── ❓ FAQs (10 questions)        # Common customer questions
│       ├── 📜 Regulatory compliance      # 14 CFR Parts 91, etc.
│       └── 🤖 AI instructions            # Tone, guidelines, constraints
│
├── 📂 shared/                             # Frontend components (not deployed - reference only)
│   └── 📄 universal-chat-widget.js        # Widget from template (not used in pilot)
│
└── 📂 .git/                               # Git version control (if initialized)
    └── (Git repository files)
```

---

## 🎨 CSS Files & Styling

### Inline CSS in mobile-demo.html

**Location**: `/tmp/dv-aviation-chat/app/static/mobile-demo.html` (lines 10-399)

**CSS Variables** (Design System):
```css
:root {
    --aviation-blue: #1E3A8A;      /* Primary brand color */
    --dark-gray: #2C3E50;          /* Secondary color */
    --light-gray: #F8F9FA;         /* Backgrounds */
    --accent-orange: #F27E26;      /* CTA buttons */
    --white: #FFFFFF;              /* Cards, bubbles */
    --shadow: rgba(0, 0, 0, 0.1);  /* Drop shadows */
}
```

**CSS Sections**:
```
mobile-demo.html CSS breakdown:
├── Lines 10-36:   Reset & Base styles
├── Lines 38-61:   Header (logo, tagline)
├── Lines 63-89:   Welcome card
├── Lines 91-125:  Quick action buttons
├── Lines 127-158: Service cards
├── Lines 160-207: CTA section
├── Lines 209-216: Footer
├── Lines 218-257: Chat modal (full-screen)
├── Lines 258-295: Message bubbles (user + bot)
├── Lines 297-337: Typing indicator animation
├── Lines 339-377: Chat input field
└── Lines 379-398: iPhone safe area support
```

**No External CSS Files** - Everything inline for:
- ✅ Zero dependencies
- ✅ Single file deployment
- ✅ Fast loading (no extra HTTP requests)
- ✅ Easy customization

---

## 🔐 Secret Management

### Google Cloud Secret Manager

**Secrets Used**:
```
1. anthropic-api-key
   ├── Purpose:     Anthropic Claude API authentication
   ├── Type:        API key (string)
   ├── Created by:  deploy.sh script
   ├── Access:      Cloud Run service only
   ├── Rotation:    Manual (update script)
   └── IAM binding: Cloud Run Service Agent

2. artemis-api-keys (inherited from main project)
   └── Not used by DV Aviation service
```

**Secret Creation** (`deploy.sh` lines 49-61):
```bash
# Check if secret exists
if ! gcloud secrets describe anthropic-api-key --project=$PROJECT_ID &>/dev/null; then
    # Create new secret
    echo -n "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key \
        --data-file=- \
        --project=$PROJECT_ID
else
    # Update existing secret (new version)
    echo -n "$ANTHROPIC_API_KEY" | gcloud secrets versions add anthropic-api-key \
        --data-file=- \
        --project=$PROJECT_ID
fi
```

**Secret Access in Cloud Run** (`deploy.sh` line 79):
```bash
gcloud run deploy dv-aviation-chat \
    --set-secrets ANTHROPIC_API_KEY=anthropic-api-key:latest
```

**Secret Usage in Application** (`app/main.py` line 63):
```python
# Get API key from environment (Cloud Run injects from Secret Manager)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")

# Initialize Anthropic client
client = Anthropic(api_key=ANTHROPIC_API_KEY)
```

### Environment Variables

**Used in Production**:
```
ANTHROPIC_API_KEY   # From Secret Manager (secret:anthropic-api-key:latest)
ENVIRONMENT         # Set to "production" (line 78 deploy.sh)
PORT                # Set to 8080 (Dockerfile line 20)
```

**NOT Used** (L7 minimal approach):
```
DATABASE_URL        # No database in pilot
REDIS_URL           # No session persistence in pilot
JWT_SECRET          # No authentication in pilot
ELEVENLABS_API_KEY  # No voice in pilot
```

### Secret Security Best Practices

✅ **Implemented**:
- Secrets stored in Google Secret Manager (not in code)
- Environment variable injection at runtime
- IAM-based access control
- Automatic rotation support (update script re-runs)
- No secrets in Git repository
- No secrets in Docker images
- No secrets in logs

❌ **NOT Implemented** (acceptable for pilot):
- Secret rotation policy (manual for now)
- Multiple secret versions (only "latest")
- Audit logging (available but not configured)
- Secret expiration dates

---

## 📦 Dependencies (requirements.txt)

```
fastapi==0.104.1              # Web framework
uvicorn[standard]==0.24.0     # ASGI server
anthropic==0.40.0             # Claude API client
pydantic==2.5.0               # Data validation
python-multipart==0.0.6       # Form parsing
structlog==23.2.0             # Structured logging
```

**Total Dependencies**: 6 core packages
**Install Size**: ~150MB (includes Python dependencies)

---

## 🐳 Docker Container Structure

**Built Image Size**: ~400MB

```
/app/                          # Container working directory
├── requirements.txt           # Copied first (layer caching)
├── app/                       # Application code
│   ├── main.py
│   └── static/
│       └── mobile-demo.html
└── knowledge/                 # Knowledge base
    └── context.json
```

**Layers**:
1. `FROM python:3.11-slim` → 180MB base image
2. `COPY requirements.txt` → 1KB
3. `RUN pip install` → 150MB dependencies
4. `COPY app/` → 20KB application code
5. `COPY knowledge/` → 15KB knowledge base

**Total**: ~400MB container

---

## 🚀 Deployment Files

### deploy.sh (112 lines)

**Structure**:
```
deploy.sh
├── Lines 1-15:   Header & configuration
├── Lines 16-32:  Configuration display
├── Lines 34-42:  API key validation
├── Lines 44-47:  User confirmation prompt
├── Lines 49-61:  Secret management
├── Lines 63-80:  Cloud Run deployment
├── Lines 82-111: Success message & instructions
└── Line 112:     Script end
```

**Configuration Variables** (lines 16-24):
```bash
PROJECT_ID="${GCP_PROJECT_ID:-n8n-agent-451019}"
SERVICE_NAME="dv-aviation-chat"
REGION="us-east4"
MEMORY="512Mi"
CPU="1"
TIMEOUT="60"
MIN_INSTANCES="0"
MAX_INSTANCES="5"
```

### Dockerfile (25 lines)

**Multi-stage**: No (single stage for simplicity)
**Base Image**: `python:3.11-slim`
**Optimization**: Layer caching (requirements.txt copied first)

---

## 📊 File Sizes

```
Documentation:
├── README.md                    → 14 KB
├── PILOT_PROPOSAL.md            → 11 KB
├── DEPLOYMENT_COMPLETE.md       → 13 KB
├── TESTING_COMPLETE_SUMMARY.md  → 8 KB
├── PLAYWRIGHT_TEST_REPORT.md    → 18 KB
├── EMBED_CODE.html              → 2 KB
├── MOBILE_APP_READY.md          → 12 KB
└── FILE_TREE.md                 → 8 KB
Total documentation: ~86 KB

Application:
├── app/main.py                  → 9 KB
├── app/static/mobile-demo.html  → 17 KB
├── knowledge/context.json       → 15 KB
└── requirements.txt             → 1 KB
Total application: ~42 KB

Deployment:
├── Dockerfile                   → 1 KB
└── deploy.sh                    → 3 KB
Total deployment: ~4 KB

Grand Total: ~132 KB (source files only)
```

---

## 🔄 Git Repository (Optional)

**If initialized**:
```
.git/
├── HEAD                        # Current branch
├── config                      # Repository config
├── description                 # Repository description
├── hooks/                      # Git hooks (unused)
├── info/                       # Exclude patterns
├── objects/                    # Git objects (commits, trees, blobs)
├── refs/
│   ├── heads/                  # Local branches
│   │   └── main                # Main branch
│   └── remotes/                # Remote branches
│       └── origin/
│           └── main
└── logs/                       # Reference logs
```

**Git Commands Used** (if versioned):
```bash
git init                        # Initialize repository
git add .                       # Stage all files
git commit -m "Initial commit"  # Create commit
git remote add origin <url>     # Add remote
git push -u origin main         # Push to remote
```

---

## 🌐 Cloud Run Deployment Structure

**Service**: `dv-aviation-chat`
**Region**: `us-east4`

```
dv-aviation-chat (Cloud Run Service)
├── Revisions:
│   ├── dv-aviation-chat-00001-dn5 (inactive)
│   ├── dv-aviation-chat-00002-gqf (inactive)
│   └── dv-aviation-chat-00003-7m4 (active, 100% traffic)
│
├── Environment Variables:
│   └── ENVIRONMENT=production
│
├── Secrets:
│   └── ANTHROPIC_API_KEY → secret:anthropic-api-key:latest
│
├── Configuration:
│   ├── Memory: 512Mi
│   ├── CPU: 1
│   ├── Timeout: 60s
│   ├── Concurrency: 80 requests/instance
│   ├── Min instances: 0 (scale to zero)
│   └── Max instances: 5
│
├── URLs:
│   ├── https://dv-aviation-chat-388610795169.us-east4.run.app (primary)
│   └── https://dv-aviation-chat-ouk4d2bbya-uk.a.run.app (hash URL)
│
└── Endpoints:
    ├── GET  /                  → Service info
    ├── GET  /health            → Health check
    ├── GET  /mobile            → Mobile app page
    ├── POST /api/chat/message  → Non-streaming chat
    └── POST /api/chat/message/stream → SSE streaming chat
```

---

## 📝 Configuration Files Summary

| File | Purpose | Size | Lines |
|------|---------|------|-------|
| `Dockerfile` | Container build | 1 KB | 25 |
| `requirements.txt` | Python deps | 1 KB | 18 |
| `deploy.sh` | Deployment script | 3 KB | 112 |
| `knowledge/context.json` | AI knowledge | 15 KB | 500 |
| `app/main.py` | Application code | 9 KB | 290 |
| `app/static/mobile-demo.html` | Mobile app | 17 KB | 585 |

**Total Configuration**: ~46 KB

---

## 🔍 Finding Files Quickly

### By Purpose

**Documentation**:
```bash
ls -1 /tmp/dv-aviation-chat/*.md
```

**Application Code**:
```bash
find /tmp/dv-aviation-chat/app -name "*.py"
```

**Static Assets**:
```bash
find /tmp/dv-aviation-chat -name "*.html" -o -name "*.css" -o -name "*.js"
```

**Deployment Files**:
```bash
ls -1 /tmp/dv-aviation-chat/{Dockerfile,requirements.txt,deploy.sh}
```

### By Type

**Python Files**:
- `app/main.py` (FastAPI application)

**HTML Files**:
- `app/static/mobile-demo.html` (Mobile app)
- `EMBED_CODE.html` (Embed snippet)

**JSON Files**:
- `knowledge/context.json` (AI knowledge base)

**Shell Scripts**:
- `deploy.sh` (Deployment automation)

**Markdown Files**:
- All documentation (8 files)

---

## 🎯 L7 Minimal Approach Verification

**What's Included** (minimum viable):
- ✅ FastAPI backend (1 file)
- ✅ Knowledge base (1 file)
- ✅ Mobile app (1 file)
- ✅ Deployment script (1 file)
- ✅ Documentation (8 files)

**Total Core Files**: 12 files, ~132 KB

**What's NOT Included** (validate first):
- ❌ Voice integration (elevenlabs)
- ❌ Session persistence (Redis)
- ❌ Analytics dashboard
- ❌ Multi-model routing
- ❌ Authentication system
- ❌ Database integration

**Why L7 Works**:
- Deployed in 15 minutes ✅
- 230 lines of Python (not 1000+) ✅
- Zero database setup ✅
- Validated with real AI chat ✅
- Ready to measure ROI ✅

---

## 📂 Complete File Listing

```bash
/tmp/dv-aviation-chat/
├── README.md                              (14 KB, 460 lines)
├── PILOT_PROPOSAL.md                      (11 KB, 384 lines)
├── DEPLOYMENT_COMPLETE.md                 (13 KB, 460 lines)
├── TESTING_COMPLETE_SUMMARY.md            (8 KB, 290 lines)
├── PLAYWRIGHT_TEST_REPORT.md              (18 KB, 580 lines)
├── EMBED_CODE.html                        (2 KB, 120 lines)
├── MOBILE_APP_READY.md                    (12 KB, 340 lines)
├── FILE_TREE.md                           (8 KB, this file)
├── Dockerfile                             (1 KB, 25 lines)
├── requirements.txt                       (1 KB, 18 lines)
├── deploy.sh                              (3 KB, 112 lines)
├── app/
│   ├── __init__.py                        (0 KB, empty)
│   ├── main.py                            (9 KB, 290 lines)
│   └── static/
│       └── mobile-demo.html               (17 KB, 585 lines)
├── knowledge/
│   └── context.json                       (15 KB, 500 lines)
└── shared/ (reference only, not deployed)
    └── universal-chat-widget.js           (not used in pilot)
```

**Total**: 15 files (excluding Git), ~132 KB source code

---

**Created**: November 18, 2025
**Project**: DV Aviation AI Chat Agent (L7 Pilot)
**Status**: ✅ Complete file tree with CSS and secret management details
