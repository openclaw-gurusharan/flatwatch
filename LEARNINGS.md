# FlatWatch Project Learnings

**Project:** Society Cash Transparency System
**Date:** 2026-01-21
**Status:** COMPLETE ✅
**Features:** 26/26 implemented
**Tests:** 105/105 passing

---

## Architecture Decisions

### Frontend Stack

- **Framework:** Next.js 16 with App Router + TypeScript
- **Styling:** Tailwind CSS with custom DRAMS design tokens
- **State:** Server components for performance, client components for interactivity
- **Rationale:** App Router for better data fetching, TypeScript for type safety

### Backend Stack

- **Framework:** FastAPI (chosen over Flask for async support)
- **Database:** SQLite with foreign key relationships
- **Server:** Uvicorn ASGI
- **Rationale:** Async/await patterns, modern Python, automatic OpenAPI docs

### DRAMS Design System

```css
--color-orange-primary: rgb(255, 97, 26)
--color-gray-track: rgb(238, 238, 238)
--radius-pill: 48px
--radius-card: 20px
--easing-primary: cubic-bezier(0.16, 1, 0.3, 1)
```

Mobile-first responsive utilities built on Tailwind.

---

## POC Mock Patterns

**All external integrations mocked for POC:**

| Service | Mock Implementation |
|---------|-------------------|
| Firebase Auth | JWT with MOCK_USERS dict |
| Razorpay | Mock transaction generator |
| OCR | Filename-based mock extraction |
| Claude Agent SDK | Keyword-based mock responses |
| Email | Console logging (EmailService class) |

**Benefits:**

- No API key dependencies
- Predictable test data
- Fast development iteration
- Clear upgrade path to production

---

## Code Patterns Learned

### SQLite Row Access

```python
# WRONG - Row has no .get() method
result.get("optional_field")

# RIGHT - Convert to dict first
row_dict = dict(row)
row_dict.get("optional_field")
```

### Pydantic v2 Configuration

```python
# OLD (deprecated)
class Config:
    from_attributes = True

# NEW (Pydantic v2)
model_config = {"from_attributes": True}
```

### Datetime Handling

```python
# OLD (deprecated)
datetime.utcnow()

# NEW (Python 3.12+)
datetime.now(timezone.utc)
```

---

## Testing Patterns

### Database Fixtures

```python
@pytest.fixture(autouse=True)
def setup_database():
    """Initialize database before each test."""
    init_db()
    yield
    # Cleanup
    db_path = get_db_path()
    if db_path.exists():
        os.remove(db_path)
```

### Test Organization

- 92 backend tests across 11 test files
- 13 frontend tests across 3 test suites
- Each feature has dedicated test file
- autouse fixtures ensure clean state

---

## Security Patterns

### AES-256 Encryption

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

aesgcm = AESGCM(ENCRYPTION_KEY)
nonce = os.urandom(12)  # 96-bit for GCM
ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
# Return base64(nonce + ciphertext)
```

### Immutable Audit Trails

- No DELETE endpoint for audit logs
- All actions logged with user_id, ip_address, timestamp
- Foreign key to users for attribution

### Role Hierarchy

```python
class Role(IntEnum):
    RESIDENT = 0
    ADMIN = 1
    SUPER_ADMIN = 2
```

---

## Deployment Patterns

### Frontend (Vercel)

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs"
}
```

### Backend (Render)

```yaml
runtime: python
buildCommand: pip install -r requirements.txt
startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### CI/CD (GitHub Actions)

```yaml
jobs:
  backend-tests:
    - pip install pytest
    - pytest tests/ --cov=app
  frontend-tests:
    - npm ci
    - npm test
    - npm run build
```

---

## Accessibility (WCAG 2.1)

- Skip link for keyboard navigation
- LiveRegion for screen reader announcements
- VisuallyHidden for sr-only content
- focus-visible indicators (2px solid orange)
- High contrast mode support
- prefers-reduced-motion respected
- Touch targets minimum 44x44px

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `Row has no attribute 'get'` | Convert to dict: `dict(row)` |
| `utcnow() deprecated` | Use `datetime.now(timezone.utc)` |
| `Config class deprecated` | Use `model_config = {...}` |
| Tests fail with "no such table" | Add `@pytest.fixture(autouse=True)` with `init_db()` |
| Port already in use | `lsof -ti:PORT | xargs kill -9` |

---

## Project Statistics

| Metric | Count |
|--------|-------|
| Total Features | 26 |
| MVP Features | 14 |
| Core Features | 10 |
| Full Features | 4 |
| Backend Tests | 92 |
| Frontend Tests | 13 |
| Total Tests | 105 |
| Backend Files | ~30 |
| Frontend Files | ~20 |
| Commits | ~25 |

---

## Files to Reference for Future Projects

- `frontend/src/app/globals.css` - DRAMS design tokens
- `backend/app/encryption.py` - AES-256 implementation
- `backend/app/audit.py` - Audit logging pattern
- `backend/app/rbac.py` - Role-based access control
- `.github/workflows/ci.yml` - CI/CD template
- `DEPLOYMENT.md` - Deployment guide

---

## Upgrade Path to Production

1. **Replace POC mocks:**
   - Firebase Auth → Real Firebase SDK
   - Razorpay → Razorpay SDK
   - OCR → Tesseract/Google Cloud Vision
   - Claude Agent SDK → Real Agent SDK

2. **Security:**
   - Move ENCRYPTION_KEY to env var (KMS/Vault)
   - Use real JWT secrets
   - Enable HTTPS only
   - Add rate limiting

3. **Database:**
   - Migrate to PostgreSQL for production
   - Add connection pooling
   - Enable WAL mode

4. **Monitoring:**
   - Add Sentry for error tracking
   - Implement health check endpoints
   - Set up log aggregation

---

**Project URL:** github.com/[user]/society-transparency-system
**License:** MIT
