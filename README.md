# FitPlan - AI Personalized Workout & Diet Planner 🏋️‍♀️🥗

FitPlan is an intelligent, full-stack web application that generates highly personalized 7-day workout and Indian diet plans. It uses Google's Gemini AI to analyze a user's body metrics, fitness goals, activity levels, diet preferences, and equipment availability to output custom routines and meals.

![FitPlan Preview](https://via.placeholder.com/1200x600.png?text=FitPlan+-+Your+Personal+AI+Fitness+Coach)

## ✨ Features

- **Auth & Security:** Secure JWT-based authentication with refresh token rotation and in-memory access token storage.
- **7-Step Onboarding:** Comprehensive wizard to collect Age, Gender, Height, Weight, Goal, Activity Level, Diet Preferences, Allergies, and Budget.
- **AI Workout Generation:** Custom 7-day routines tailored to available equipment and goals with proper rest days.
- **AI Diet Generation:** Custom 7-day Indian meal plans accurately calculated to match the user's Total Daily Energy Expenditure (TDEE).
- **Meal Swapping:** Don't like a meal? Swap out individual meals with a single click to generate a new AI recommendation.
- **Caching & Rate Limiting:** Redis-backed caching ensures instant plan loading after the first generation, alongside IP and user-based rate limiting to prevent API abuse.
- **Responsive UI:** A beautifully designed, mobile-responsive dashboard using Tailwind CSS and micro-animations.

---

## 🛠️ Tech Stack

**Frontend:**
- React 18 + Vite
- Tailwind CSS (Vanilla CSS for custom tokens & theming)
- Zustand (Global State Management)
- Axios (API Interceptors for silent auth refreshing)
- React Router DOM

**Backend:**
- Python 3.10+ & FastAPI
- PostgreSQL (Primary Database)
- SQLAlchemy + Alembic (ORM & Migrations)
- Redis (Caching & Rate Limiting)
- Google Gemini AI SDK (LLM integration)

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- PostgreSQL installed and running
- Redis installed and running
- Google Gemini API Key

### 1. Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the `backend` directory with the following variables:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/workout_planner_db
   REDIS_URL=redis://localhost:6379/0
   
   SECRET_KEY=your_super_secret_key
   REFRESH_SECRET_KEY=your_refresh_secret_key
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REFRESH_TOKEN_EXPIRE_DAYS=7

   GEMINI_API_KEY=your_gemini_api_key_here
   
   FRONTEND_URL=http://localhost:5173
   ```

5. **Run Migrations & Start Server:**
   ```bash
   alembic upgrade head
   uvicorn app.main:app --reload
   ```
   The backend will be available at `http://localhost:8000`. API docs can be viewed at `http://localhost:8000/docs`.

### 2. Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Environment Variables:**
   Create a `.env` file in the `frontend` directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

4. **Start the Development Server:**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`.

---

## 📁 Project Structure

```text
workout_planner/
├── backend/
│   ├── app/
│   │   ├── api/            # API routers (auth, users, workout, diet)
│   │   ├── core/           # Security, config, and DB connections
│   │   ├── models/         # SQLAlchemy DB models
│   │   ├── schemas/        # Pydantic schemas for validation
│   │   ├── services/       # Business logic (AI Service, Auth Service)
│   │   └── utils/          # Prompt builders, helpers
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── components/     # Reusable UI components (Buttons, Cards, Modals)
    │   ├── hooks/          # Custom React hooks (usePlan, useAuth)
    │   ├── pages/          # Main application views (Dashboard, Onboarding)
    │   ├── routes/         # Protected and public route wrappers
    │   ├── services/       # Axios API callers
    │   └── store/          # Zustand state slices
    ├── tailwind.config.js  # Custom theme & color palette
    └── package.json        # Node dependencies
```

---

## 🤝 Contributing
1. Fork the project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
