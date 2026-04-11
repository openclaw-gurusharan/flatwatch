# FlatWatch – Society Transparency System

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/openclaw-gurusharan/flatwatch)

> AI-powered web application for financial transparency and accountability in Indian housing societies.

A proof-of-concept (POC) application designed to enhance transparency in housing society financial management through automated transaction tracking, receipt verification, AI-powered queries, and a public dashboard for accountability.

## 🌟 Features

| Feature | Description |
|---------|-------------|
| **Live Money Feed** | Real-time transaction ingestion via Razorpay/MyGate integration |
| **Receipt Snap** | Upload receipts (PDF, images, Excel/CSV) with OCR extraction and auto-matching |
| **Chat Guard** | AI-powered natural language queries with bye-laws compliance context |
| **Challenge Mode** | Dispute suspicious transactions with 48-hour resolution timer |
| **Shame Dashboard** | Public-facing financial metrics with transaction attribution |
| **Daily AI Analysis** | Automated scans for discrepancies and mismatched entries |

## 🏗️ Architecture

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 16, React 19, Tailwind CSS 4, dRAMS Design |
| **Backend** | FastAPI, Python 3.12, SQLite |
| **Auth** | SSO via aadharcha.in (identity provider) |
| **AI** | Claude Agent SDK |
| **OCR** | Google Cloud Vision / Tesseract |
| **Database** | SQLite (POC), PostgreSQL (production) |

### Project Structure

```
society-transparency-system/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/              # Next.js app router pages
│   │   ├── components/      # React components
│   │   └── lib/             # Utilities (auth, API client)
│   └── package.json
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── routers/         # API endpoints
│   │   ├── models.py        # Database models
│   │   └── main.py          # Application entry
│   ├── data/                # SQLite database
│   └── requirements.txt
├── .claude/                 # Claude Code configuration
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.12+
- npm or pnpm
- SSO account on [aadharcha.in](https://aadharcha.in)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/ingpoc/flatwatch.git
   cd flatwatch
   ```

2. **Install frontend dependencies**

   ```bash
   cd frontend
   npm install
   ```

3. **Install backend dependencies**

   ```bash
   cd ../backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create `frontend/.env.local`:

   ```bash
   NEXT_PUBLIC_API_URL=http://127.0.0.1:43104
   NEXT_PUBLIC_IDENTITY_URL=http://127.0.0.1:43100
   ```

### Development

1. **Start the backend**

   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --reload
   ```

2. **Start the frontend**

   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application**
   - Frontend: <http://127.0.0.1:43105>
   - Backend API: <http://127.0.0.1:43104>
   - API Docs: <http://127.0.0.1:43104/api/docs>

## 🔐 Authentication

FlatWatch uses SSO (Single Sign-On) via [aadharcha.in](https://aadharcha.in):

- **Protected Routes**: `/dashboard`, `/receipts`, `/challenges`, `/chat`
- **Auto-Redirect**: Unauthenticated users are redirected to SSO login
- **Session Validation**: Sessions validated before each API call
- **User Context**: `useAuth()` hook provides user state and auth functions

### Auth Hook Usage

```tsx
import { useAuth } from '@/lib/auth';
import { ProtectedRoute } from '@/lib/ProtectedRoute';

function MyComponent() {
  const { user, loading, login, logout } = useAuth();

  if (loading) return <div>Loading...</div>;

  return (
    <ProtectedRoute>
      <div>Welcome, {user?.name}</div>
    </ProtectedRoute>
  );
}
```

## 📡 API Usage

All API calls include automatic session validation and `X-User-ID` header:

```typescript
import { transactionsApi, receiptsApi } from '@/lib/api';

// List transactions (session auto-validated)
const txns = await transactionsApi.list({ limit: 10 });

// Upload receipt
await receiptsApi.upload(file);

// Create challenge
await challengesApi.create(transactionId, "Reason for challenge");
```

## 🧪 Testing

### Frontend Tests

```bash
cd frontend
npm test
```

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest
```

### Test Coverage

- Auth hook: 14 tests ✅
- API wrapper: 20 tests ✅
- Backend auth: 9 tests ✅

## 🔒 Security Features

- **AES-256 Encryption** for sensitive data
- **Immutable Audit Trails** for all actions
- **Role-Based Access Control** (Resident, Admin, Super-admin)
- **SSO Integration** with aadharcha.in
- **Credentials: include** for cookie handling
- **WCAG 2.1** accessibility compliance

## 📱 Pages

| Route | Page | Access |
|-------|------|--------|
| `/` | Landing page | Public |
| `/dashboard` | Financial summary & transactions | Authenticated |
| `/receipts` | Upload & manage receipts | Authenticated |
| `/challenges` | Create & track disputes | Authenticated |
| `/chat` | AI-powered financial queries | Authenticated |
| `/notifications` | Notification preferences | Authenticated |

## 🛣️ Roadmap

### POC (Current)

- Single society support (~650 flats)
- Razorpay/MyGate integration
- Basic AI analysis
- SQLite database

### Future Versions

- **v1.1**: Multi-society support, advanced ML anomaly detection
- **v2.0**: Mobile app, additional gateway integrations (PhonePe)

## 📄 License

This project is proprietary software.

## 👥 Contributing

This is a private project. For inquiries, contact the maintainers.

---

**Built with ❤️ for housing society transparency**
