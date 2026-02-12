# PostureScore - Real-Time Posture Analysis Web App

## Context

Build a full-stack web application that uses a user's webcam to analyze their posture in real-time, provide a score (0-100), and recommend corrective exercises. The app needs authentication, a freemium monetization model, and uses Django (ASGI) + Vue 3 (Vuetify 3). The project directory (`/home/andy/Desktop/posture_score`) is currently empty.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend Framework** | Django 4.2+ with Django REST Framework |
| **Real-time Server** | Django Channels 4.3 + Daphne (ASGI) |
| **Pose Estimation** | MediaPipe Pose (CPU-friendly, ~30ms/frame) |
| **Frame Processing** | OpenCV (headless) + NumPy |
| **Authentication** | SimpleJWT (access + refresh tokens) |
| **Database** | PostgreSQL (via Docker) |
| **Channel Layer** | Redis (via Docker) |
| **Frontend Framework** | Vue 3 + Vuetify 3 (scaffolded via Vite) |
| **State Management** | Pinia |
| **Webcam Access** | navigator.mediaDevices.getUserMedia |
| **Real-time Transport** | WebSocket (base64 JPEG frames at ~15fps) |
| **Payments** | Stripe (Checkout + Webhooks) |
| **Containerization** | Docker Compose (PostgreSQL, Redis, backend) |

---

## Project Structure

```
posture_score/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── posture_project/          # Django project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py               # ASGI with HTTP + WebSocket routing
│   │   └── wsgi.py
│   ├── accounts/                 # User auth & profiles
│   │   ├── models.py             # UserProfile (extends User)
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── posture/                  # Core analysis engine
│   │   ├── models.py             # PostureSession, PostureScore
│   │   ├── consumers.py          # WebSocket consumer
│   │   ├── routing.py            # WebSocket URL routing
│   │   ├── scoring.py            # Posture scoring algorithm
│   │   ├── landmark_utils.py     # MediaPipe helper functions
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── exercises/                # Exercise library & recommendations
│   │   ├── models.py             # Exercise, ExerciseCategory, UserExerciseLog
│   │   ├── recommender.py        # Recommendation engine
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── management/commands/seed_exercises.py
│   ├── subscriptions/            # Monetization & feature gating
│   │   ├── models.py             # SubscriptionPlan, UserSubscription
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── middleware/
│       └── jwt_websocket.py      # JWT auth for WebSocket connections
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── api/                  # Axios instance + interceptors
│       ├── composables/
│       │   ├── useWebcam.js      # Camera access & frame capture
│       │   └── usePostureSocket.js  # WebSocket lifecycle
│       ├── stores/               # Pinia stores (auth, posture, exercises, subscription)
│       ├── router/               # Vue Router + auth guards
│       ├── views/                # Page components
│       ├── components/           # Reusable UI components
│       └── plugins/vuetify.js
├── docker-compose.yml            # PostgreSQL + Redis
├── .gitignore
└── README.md
```

---

## API Design

### REST Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register/` | User registration |
| POST | `/api/auth/login/` | Obtain JWT pair |
| POST | `/api/auth/refresh/` | Refresh access token |
| GET/PATCH | `/api/auth/profile/` | User profile |
| GET | `/api/posture/sessions/` | List past sessions |
| GET | `/api/posture/sessions/<id>/` | Session detail + scores |
| GET | `/api/posture/stats/` | Aggregate stats & trends |
| GET | `/api/exercises/` | Exercise library (filterable) |
| GET | `/api/exercises/recommended/` | Personalized recommendations |
| GET | `/api/subscriptions/plans/` | Available plans |
| POST | `/api/subscriptions/checkout/` | Stripe checkout session |
| POST | `/api/subscriptions/webhook/` | Stripe webhook handler |

### WebSocket Endpoint

`ws/posture/analyze/?token=<JWT>` — Bidirectional real-time posture analysis

**Client sends:** `{"action": "start_session"}`, `{"action": "frame", "frame": "<base64 JPEG>"}`, `{"action": "end_session"}`

**Server responds:** `{"type": "posture_result", "score": 78.5, "details": {...}, "issues": [...], "landmarks": [...]}`

---

## Posture Scoring Algorithm

Uses **MediaPipe Pose** landmarks from a frontal webcam view. Four component scores weighted into an overall 0-100 score:

| Component | Weight | Landmarks Used | What It Measures |
|-----------|--------|---------------|-----------------|
| Forward Head Position | 30% | Ears (7,8), Shoulders (11,12) | Head jutting forward relative to shoulders |
| Shoulder Levelness | 25% | Shoulders (11,12) | Y-coordinate difference (lateral tilt) |
| Shoulder Rounding | 25% | Shoulders (11,12), Hips (23,24) | Shoulder width vs hip width ratio |
| Spine Alignment | 20% | Shoulders (11,12), Hips (23,24) | Torso angle deviation from vertical |

**Score ranges:** 85-100 Excellent (green), 70-84 Good, 55-69 Fair (amber), 40-54 Needs Work (orange), 0-39 Poor (red)

**Calibration:** 5-second initial calibration where user stands in best posture to establish personal baseline. This captures the "ideal" outline.

**DB persistence:** Scores saved every ~1 second (every 15th frame) to avoid DB overload while maintaining useful history.

---

## Live Analysis UX — Dual Outline Overlay

The user stands in front of their webcam. The live view renders two outlines on the canvas:

1. **Actual outline (dynamic):** Drawn from real-time MediaPipe landmarks — shows the user's current posture as a body outline/skeleton. Color-coded by score (green → red).
2. **Ideal outline (reference):** A semi-transparent "ghost" outline captured during the calibration step, representing the user's best posture. Stays fixed as the target.

The user can see in real-time how their current posture deviates from their ideal. Where body segments diverge from the ideal, the gap is visually highlighted (e.g. red shading or arrows). The score reflects how closely the actual outline matches the ideal.

**Server sends back:** landmarks + ideal landmarks (from calibration) + per-component scores, so the frontend can render both outlines and the deviation indicators.

---

## Frontend Pages

| View | Route | Auth | Description |
|------|-------|------|-------------|
| Landing | `/` | No | Marketing page |
| Login | `/login` | No | JWT login form |
| Register | `/register` | No | Registration form |
| Dashboard | `/dashboard` | Yes | Score gauge, 7-day trend, recent sessions, recommended exercises |
| Live Analysis | `/analyze` | Yes | Dual-outline overlay: user's actual posture outline + ideal posture outline, real-time score |
| History | `/history` | Yes | Score charts (Chart.js), session list, progress metrics |
| Exercise Library | `/exercises` | Yes | Filterable exercise grid |
| Exercise Detail | `/exercises/:id` | Yes | Instructions, video, "mark complete" |
| Pricing | `/pricing` | No | Subscription plan comparison |
| Settings | `/settings` | Yes | Profile, notifications, preferences |

---

## Monetization Strategy

### 1. Freemium SaaS Subscriptions (Primary Revenue)

| Feature | Free | Pro ($7.99/mo) | Premium ($14.99/mo) |
|---------|------|-----------------|---------------------|
| Sessions/day | 2 (5 min max) | Unlimited | Unlimited |
| Score breakdown | Overall only | Full 4-component | Full + trends |
| History | 7 days | 90 days | Unlimited |
| Exercise library | 10 basic | 50+ full | 50+ full |
| Recommendations | Top 3 generic | Issue-specific | AI-curated plans |
| Export reports | No | PDF/CSV | PDF/CSV + branded |
| Reminders | No | Email | Email + push |

### 2. Corporate Wellness Packages (B2B)
- Per-seat pricing ($5/employee/month, min 10 seats)
- Admin dashboard with aggregate posture trends
- SSO integration, compliance reporting

### 3. One-Time Posture Reports ($4.99/report)
- Comprehensive PDF with annotated screenshots, angle measurements
- Personalized 4-week exercise program

### 4. Affiliate Partnerships
- Ergonomic product recommendations (standing desks, chairs, lumbar supports)
- Physical therapy platform referrals

### 5. Premium Content
- Expert video tutorials from physical therapists
- Guided multi-week posture correction programs

---

## Implementation Phases

### Phase 1: Backend Foundation + Auth ✅ COMPLETE
- Commit `0115209` — 48 files, 1507 lines
- All 12 REST endpoints smoke tested and passing
- Auth (register, login, refresh, profile), stub views, Docker Compose, ASGI

### Phase 2: Posture Analysis Engine ✅ COMPLETE
- MediaPipe PoseLandmarker (Tasks API v0.10.32) with lite model
- `PostureScorer` class: 4-component weighted scoring (head 30%, shoulder levelness 25%, rounding 25%, spine 20%)
- Full WebSocket consumer: session lifecycle, calibration flow (45 frames averaged), frame analysis, DB persistence every 15 frames
- `landmark_utils.py`: decode base64 frames, extract/serialize landmarks
- Calibration-based scoring: compares current pose against user's ideal baseline
- Dual landmark response: current + ideal landmarks sent to frontend for overlay
- StatsView updated to use TruncDate (replaced deprecated .extra())

### Phase 3: Frontend + Live Analysis ✅ COMPLETE
- 16 source files, ~1,430 lines
- Vue 3 + Vuetify 3 + Vite + Pinia + Vue Router
- Axios with JWT interceptors (auto-refresh on 401)
- Auth views (login, register) with form validation
- `useWebcam` composable: camera access, base64 JPEG frame capture
- `usePostureSocket` composable: WebSocket lifecycle, throttled frame sending at 15fps
- `LiveAnalysisView`: dual skeleton overlay (current + ideal ghost), real-time score gauge, per-component breakdown, calibration flow, session summary
- App shell: Vuetify app bar + nav drawer, auth-aware routing with guards
- Additional views: Landing, Dashboard, History, Exercises

### Phase 4: Exercise Recommendations ✅ COMPLETE
- `recommender.py`: analyzes user's last 5 sessions, finds weak components (<70), maps to target exercises prioritized by severity, falls back to general exercises
- `seed_exercises.py`: management command with 36 exercises across 4 categories (Stretching, Strengthening, Mobility, Awareness) and 5 target issues (forward_head ×8, shoulder_level ×6, shoulder_round ×8, spine_align ×8, general ×6). Supports `--clear` flag.
- Updated `RecommendedExercisesView` with real recommender logic, added `ExerciseLogCreateView` + `ExerciseLogListView`, added category filter to exercise list
- Frontend `ExercisesView`: 3-column filters (target issue, difficulty, category), recommended section at top, detail dialog with instructions + "Mark Complete" button
- Dashboard: recommended exercises card (top 3 targeted exercises)
- LiveAnalysisView: shows up to 4 recommended exercises after session ends

### Phase 5: History & Analytics Dashboard (files: history views, ScoreChart.vue, posture/views.py stats endpoint)
1. Implement stats aggregation endpoint
2. Build history view with Chart.js line charts (7d/30d/90d)
3. Build session list with expandable score timelines
4. Enhance dashboard with score gauge, trend chart, streak counter

### Phase 6: Monetization & Polish (files: subscriptions/*, PricingView.vue, middleware)
1. Set up Stripe products/prices
2. Implement checkout + webhook endpoints
3. Build feature gating (session limits, history limits, premium content locks)
4. Build pricing page with plan comparison
5. Add dark mode, PWA support
6. Production config (env vars, HTTPS, static files)

---

## Verification Plan

1. **Auth flow:** Register → login → verify JWT in localStorage → access protected route → token refresh on expiry
2. **Live analysis:** Start session → grant camera permission → see webcam feed → verify skeleton overlay draws on landmarks → check score updates in real-time → end session → verify session saved to DB
3. **Exercise recommendations:** Complete a session with known posture issues → check `/api/exercises/recommended/` returns exercises targeting those issues
4. **History:** Run multiple sessions → verify charts show correct data points → test date range filtering
5. **Monetization:** Create free account → hit session limit → verify upgrade prompt → test Stripe checkout flow → verify feature unlocks after subscription
6. **WebSocket auth:** Attempt WS connection without token → verify rejection → connect with valid token → verify acceptance
