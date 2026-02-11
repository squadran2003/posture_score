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

**Calibration:** 5-second initial calibration where user sits in best posture to establish personal baseline.

**DB persistence:** Scores saved every ~1 second (every 15th frame) to avoid DB overload while maintaining useful history.

---

## Frontend Pages

| View | Route | Auth | Description |
|------|-------|------|-------------|
| Landing | `/` | No | Marketing page |
| Login | `/login` | No | JWT login form |
| Register | `/register` | No | Registration form |
| Dashboard | `/dashboard` | Yes | Score gauge, 7-day trend, recent sessions, recommended exercises |
| Live Analysis | `/analyze` | Yes | Webcam feed + skeleton overlay + real-time score + alerts |
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

### Phase 1: Backend Foundation + Auth (files: settings.py, accounts/*, asgi.py)
1. Init git repo, create `.gitignore`
2. Create Django project + all 4 apps
3. Configure settings: DRF, SimpleJWT, Channels, CORS, ASGI
4. Write all database models, run migrations
5. Implement auth endpoints (register, login, refresh, profile)
6. Set up `docker-compose.yml` (PostgreSQL + Redis)
7. Set up `requirements.txt`

### Phase 2: Posture Analysis Engine (files: scoring.py, landmark_utils.py, consumers.py, routing.py, jwt_websocket.py)
1. Implement `PostureScorer` class with MediaPipe + 4 component score calculations
2. Implement landmark utility helpers
3. Build WebSocket consumer (frame receive → analyze → respond)
4. Build JWT WebSocket auth middleware
5. Configure ASGI routing (HTTP + WebSocket)
6. Implement REST endpoints for session history and stats

### Phase 3: Frontend + Live Analysis (files: all frontend/src/*)
1. Scaffold Vue 3 + Vuetify 3 + Vite project
2. Set up Axios with JWT interceptors, Pinia stores, Vue Router + auth guards
3. Build auth views (login, register)
4. Implement `useWebcam` composable (camera access, frame capture)
5. Implement `usePostureSocket` composable (WebSocket lifecycle, throttled frame sending)
6. Build `LiveAnalysisView` with webcam feed, skeleton overlay, score gauge, posture alerts

### Phase 4: Exercise Recommendations (files: exercises/*, recommender.py, seed_exercises.py)
1. Build recommendation engine (maps detected issues → exercises)
2. Implement exercise REST endpoints
3. Create seed command with 30-40 exercises
4. Build exercise library view, cards, detail view
5. Integrate recommendations into dashboard + end-of-session summary

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
