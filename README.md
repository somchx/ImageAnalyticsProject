# Non-Destructive Grilling Analytics and Burn Detection with Alarm System

## Project Overview

A complete full-stack web application for real-time pork grilling analysis using **only traditional image processing techniques**. The system captures video/image input, removes smoke interference via **Dark Channel Prior (DCP)** dehazing, extracts **CIELAB color metrics**, applies a **rule-based state machine** to classify doneness stages, and triggers **Telegram Bot** alerts when the meat needs attention.

> **Academic Constraint: Strictly NO AI / NO Machine Learning / NO Deep Learning.**
> All analysis is performed using classical computer vision: color space conversion, morphological operations, contour analysis, thresholding, and rule-based logic.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                  │
│  Dashboard │ Live Monitor │ Upload │ History │ Settings       │
│  Recharts charts │ WebSocket client │ Zustand state stores    │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP REST + WebSocket
┌──────────────────────────▼──────────────────────────────────┐
│                    BACKEND (Python + FastAPI)                 │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                   CV Pipeline                          │  │
│  │  Frame → DCP Dehaze → ROI Extract → CIELAB Convert     │  │
│  │  → Compute Metrics → Temporal Smooth → State Machine   │  │
│  │  → Alert Engine → Annotate Frame → JSON Response       │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  Services: SessionService │ FrameService │ TelegramService    │
│  Storage:  SQLite (SQLAlchemy) + CSV files per session       │
└──────────────────────────┬──────────────────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
  Webcam (WS)        Video Upload         Image Upload
  (real-time)     (BackgroundTask)      (single frame)
```

---

## Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) Docker + Docker Compose

---

## Installation & Running

### Without Docker

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env to set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID if desired
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

The frontend proxies `/api` and `/ws` requests to `localhost:8000`.

### With Docker Compose

```bash
# Edit .env in project root with Telegram credentials
docker compose up --build
```

Open **http://localhost** in your browser.

---

## How to Set Up Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow prompts → you get a **Bot Token** like `123456789:ABCdefGhIJK...`
3. Start a chat with your bot, then get your **Chat ID**:
   - Send any message to the bot
   - Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Find `"chat": {"id": <YOUR_CHAT_ID>}`
4. In the app: go to **Settings** → enter the token and chat ID → enable Telegram → Save
5. Click **Send Test Message** to verify

---

## Image Processing Pipeline

Each frame goes through 7 steps:

### 1. Frame Normalization
Resize to max 1280px on the longest side (maintains aspect ratio), then apply Gaussian blur (3×3) to suppress JPEG compression noise.

### 2. Dark Channel Prior (DCP) Dehazing
Implements He et al. 2009 to remove smoke/haze interference:
- **Dark Channel**: minimum pixel over a local patch (min of min over RGB channels)
- **Atmospheric Light (A)**: estimated from the brightest 0.1% of dark-channel pixels
- **Transmission Map (t)**: `1 - ω × dark_channel(I/A)`, clamped to [t_min, 1.0]
- **Scene Radiance**: `J = (I - A) / t + A`
- Transmission is refined using a guided box-filter approximation

Without this step, smoke would artificially increase L* values and mask browning progression.

### 3. ROI Extraction
Isolates the food item from grill grates and background:
- HSV-based mask removes dark metal grates (low saturation, low value)
- Canny edge detection + dilation removes grate line structures
- Combined exclusion mask is inverted → morphological open/close
- Largest contour kept as the main food region

### 4. CIELAB Color Space Conversion
Converts the dehazed BGR image to CIE L\*a\*b\* (perceptually uniform color space):
- **L\*** = lightness [0–100]: raw pork ≈ 68–72, well-cooked ≈ 42–50, burnt < 22
- **a\*** = red-green axis: browning increases a\* via Maillard reaction
- **b\*** = yellow-blue axis: browning increases b\* from caramelization

### 5. Per-Frame Metric Computation

| Metric | Formula | Meaning |
|--------|---------|---------|
| L\*\_mean | mean(roi\_L) | Average brightness of food surface |
| a\*\_mean | mean(roi\_a) | Average redness |
| b\*\_mean | mean(roi\_b) | Average yellowness |
| **Browning Score** | 0.5×sig\_L + 0.3×sig\_a + 0.2×sig\_b | Composite 0–1 doneness index |
| Cooked area % | pixels where L\*<55 AND a\*>4 | Fraction of surface that is browned |
| Burn risk area % | pixels where L\*<30 | Fraction of surface at risk of burning |
| Smoke density | sky-band uniformity + brightness + contrast-drop | 0–1 estimate of haze coverage |

**Browning Score sub-signals:**
- `sig_L = 1 − clip(L_mean/75, 0, 1)` — lower brightness = more cooked
- `sig_a = clip((a_mean−2)/20, 0, 1)` — more redness from Maillard browning
- `sig_b = clip((b_mean−8)/25, 0, 1)` — more yellowness from caramelization

### 6. Temporal Smoothing
A `MovingAverageSmoother` with a configurable window (default: 7 frames) reduces per-frame noise from lighting fluctuations, smoke transients, and motion blur. Only smoothed values are fed to the state machine.

### 7. State Machine + Alert Engine
See sections below.

---

## State Machine (Rule-Based)

States advance based on smoothed CIELAB metrics. A minimum hold of 5 frames is required before any forward transition (prevents rapid flicker).

```
RAW → COOKING → READY_TO_FLIP → READY → OVERCOOKED_RISK → BURNT
                     ↓ (flip detected: browning drops)
                  COOKING
```

| Transition | Condition |
|-----------|-----------|
| RAW → COOKING | L\* < 65 OR browning > 0.15 |
| COOKING → READY\_TO\_FLIP | browning ≥ 0.40 AND L\* < 52 |
| READY\_TO\_FLIP → COOKING | browning < 0.30 (flip detected: fresh side exposed) |
| READY\_TO\_FLIP → READY | browning ≥ 0.55 AND L\* < 42 |
| READY → OVERCOOKED\_RISK | browning ≥ 0.72 AND L\* < 32 |
| OVERCOOKED\_RISK → BURNT | browning ≥ 0.88 OR L\* < 22 |
| ANY → BURNT (emergency) | L\* < 18 OR burn\_risk% > 35 |

---

## Alert Logic

Alerts are triggered by the `AlertEngine` with per-code cooldown timers (default: 30 seconds) to prevent spam.

| Alert Code | Severity | Trigger | Debounce |
|-----------|---------|---------|---------|
| READY\_TO\_FLIP | WARNING | State changes to READY\_TO\_FLIP | 1 frame |
| READY | WARNING | State changes to READY | 1 frame |
| OVERCOOKED\_RISK | WARNING | State changes to OVERCOOKED\_RISK | 1 frame |
| BURNT | CRITICAL | State changes to BURNT | 1 frame |
| BURN\_RISK\_HIGH | WARNING | burn\_risk% > 10 | 3 consecutive frames |
| BURN\_RISK\_CRITICAL | CRITICAL | burn\_risk% > 20 OR L\* < 25 | 2 consecutive frames |
| SMOKE\_SPIKE | WARNING | smoke > 0.30 | 3 consecutive frames |
| SMOKE\_CRITICAL | CRITICAL | smoke > 0.55 | 2 consecutive frames |

---

## Dashboard Pages

| Page | Path | Description |
|------|------|-------------|
| Dashboard | `/` | Summary cards, 4 real-time charts, event log |
| Live Monitor | `/monitor` | Webcam feed, processed frames side-by-side, explainability |
| Upload | `/upload` | Drag-drop image/video upload + instant analysis |
| History | `/history` | Paginated list of all past sessions |
| Session Detail | `/history/:id` | Full replay charts + event timeline + CSV export |
| Settings | `/settings` | All thresholds, Telegram config, system params |

---

## CSV Data Schema

Each session produces a CSV at `data/sessions/{session_id}.csv`:

```
session_id, frame_index, timestamp_ms, source_type,
L_star_mean, L_star_std, a_star_mean, a_star_std, b_star_mean, b_star_std,
browning_score, cooked_area_pct, burn_risk_area_pct, smoke_density,
L_star_smooth, browning_smooth, cooked_area_smooth, burn_risk_smooth, smoke_smooth,
grill_state, state_changed, alert_codes, processing_time_ms, explanation
```

---

## Default Thresholds

All thresholds are configurable via the Settings page. Defaults tuned for unseasoned pork (no marinade/sauce):

| Parameter | Default |
|-----------|---------|
| L\* max for COOKING start | 65.0 |
| L\* max for READY\_TO\_FLIP | 52.0 |
| L\* max for READY | 42.0 |
| L\* max for OVERCOOKED\_RISK | 32.0 |
| L\* max for BURNT | 22.0 |
| Browning min for READY\_TO\_FLIP | 0.40 |
| Browning min for READY | 0.55 |
| Burn risk WARNING % | 10.0 |
| Smoke WARNING | 0.30 |
| Smoothing window | 7 frames |
| Alert cooldown | 30 seconds |

---

## Limitations

- **Pork only**: Thresholds calibrated for unseasoned pork. Other meats have different initial L\*, a\*, b\* values and would need recalibration.
- **No sauce or marinade**: Dark sauces (e.g., soy-based marinades) artificially lower L\* and would trigger false burn detections.
- **Lighting-dependent**: Fluorescent vs. natural vs. fire light changes L\* readings. For best results, maintain consistent ambient lighting.
- **Camera angle**: The system assumes the camera has a clear top-down or angled view of the food. Extreme angles cause ROI extraction to fail.
- **Single item**: Only one main food contour (largest) is tracked. Multi-piece grilling requires further ROI management.
- **Not certified**: This is an academic prototype. It is NOT a food safety or medical device. Do not rely on it as the sole indicator of food safety.
- **Smoke estimation is approximate**: The sky-band smoke detector assumes a clear upper-frame area. If the camera is very close to the grill, this may not hold.

---

## Future Improvements

- Camera calibration for consistent color readings under varying light
- Multi-item tracking with multiple ROI contours
- Side-to-side asymmetry detection for smarter flip timing
- Integration with a meat thermometer sensor for ground-truth validation
- LINE Messaging API integration (stub already in `line_service.py`)
- Session replay with frame scrubber and frame-by-frame inspection
- Support for other meats (chicken, beef) with separate threshold profiles
- Web-based ROI drawing tool for user-defined food regions

---

## Academic Note

This project was built for a university computer vision course under the constraint of using **only traditional image processing**:
- Dark Channel Prior (He et al., 2009)
- CIE L\*a\*b\* color space (perceptually uniform)
- Morphological operations (erosion, dilation, open, close)
- Contour analysis (OpenCV findContours)
- Rule-based threshold logic

No pretrained models, no neural networks, no ML libraries are used anywhere in the codebase.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + FastAPI + Uvicorn |
| Computer Vision | OpenCV 4.9 + NumPy |
| Frontend | React 18 + TypeScript + Vite |
| Styling | TailwindCSS |
| Charts | Recharts |
| State | Zustand |
| Storage | SQLite (SQLAlchemy) + CSV |
| Real-time | WebSocket (FastAPI native) |
| Notifications | Telegram Bot API (httpx) |
| Deployment | Docker + Docker Compose + Nginx |

# Test