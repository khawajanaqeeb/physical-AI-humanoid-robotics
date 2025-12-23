# Implementation Plan
## Feature: Docusaurus Better Auth Integration with Profile Personalization

**Branch**: `main` (all work committed directly to main, no feature branches)
**Created**: 2025-12-21
**Status**: Ready for Implementation

---

## Executive Summary

**Objective**: Integrate authentication into Docusaurus frontend to work with existing FastAPI backend, enabling personalized RAG chatbot responses based on user profiles.

**Approach**: Hybrid architecture using Better Auth client-side (React hooks/components) with existing FastAPI JWT backend.

**Scope**:
- ✅ Backend authentication already implemented - NO CHANGES except personalization service
- ⚠️ Frontend authentication UI - IMPLEMENT in Docusaurus
- ⚠️ RAG chatbot access gating - IMPLEMENT client + server enforcement
- ⚠️ Personalization service - IMPLEMENT prompt injection based on user profile

**Timeline**: 3 implementation phases (UI → Gating → Personalization)

---

## Phase 0: Research & Design ✅ COMPLETE

**Artifacts Created**:
- `research.md` - Technology decisions and architectural approach
- `data-model.md` - Database schema documentation (existing backend)
- `contracts/auth-api.yaml` - OpenAPI specification for auth endpoints
- `quickstart.md` - Quick reference guide

**Key Decisions**:
1. Better Auth client-side only (no Node.js backend)
2. Keep existing FastAPI JWT authentication
3. HTTP-only cookies for refresh tokens
4. Client + server chatbot gating
5. Profile-based RAG prompt personalization

---

## Phase 1: Frontend Authentication UI

### 1.1 Install Dependencies

**File**: `package.json`

```json
{
  "dependencies": {
    "better-auth": "^1.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
```

**Commands**:
```bash
npm install better-auth
npm install --save-dev @types/react typescript
```

### 1.2 Create Auth Client Configuration

**File**: `src/lib/auth-client.ts` (NEW)

```typescript
import { createAuthClient } from 'better-auth/react';

const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

export const authClient = createAuthClient({
  baseURL: backendUrl,
  fetchOptions: {
    credentials: 'include', // Send cookies cross-origin
  },
});

// Export hooks for use in components
export const {
  useSession,
  useSignIn,
  useSignUp,
  useSignOut,
} = authClient;
```

**Purpose**: Configure Better Auth client to call FastAPI backend endpoints

### 1.3 Create Auth Context Provider

**File**: `src/components/auth/AuthContext.tsx` (NEW)

```typescript
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useSession, useSignIn, useSignUp, useSignOut } from '@/lib/auth-client';

interface User {
  id: string;
  email: string;
  profile?: {
    software_experience: string;
    hardware_experience: string;
    interests: string[];
  };
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signin: (email: string, password: string) => Promise<void>;
  signup: (data: SignupData) => Promise<void>;
  signout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: session, isLoading } = useSession();
  const { mutateAsync: signin } = useSignIn();
  const { mutateAsync: signup } = useSignUp();
  const { mutateAsync: signout } = useSignOut();

  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (session?.user) {
      setUser(session.user);
    } else {
      setUser(null);
    }
  }, [session]);

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    signin,
    signup,
    signout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

**Purpose**: Centralized auth state management for entire app

### 1.4 Wrap App with AuthProvider

**File**: `src/theme/Root.tsx` (NEW or MODIFY if exists)

```typescript
import React from 'react';
import { AuthProvider } from '@/components/auth/AuthContext';

export default function Root({ children }) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
}
```

**Purpose**: Make auth context available to all components

### 1.5 Create Signup Form Component

**File**: `src/components/auth/SignupForm.tsx` (NEW)

```typescript
import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from '@docusaurus/router';
import './auth.css';

export default function SignupForm() {
  const { signup } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    software_experience: 'BEGINNER',
    hardware_experience: 'NONE',
    interests: [] as string[],
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-zA-Z])(?=.*[0-9])/.test(formData.password)) {
      newErrors.password = 'Password must contain letters and numbers';
    }

    // Confirm password
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords must match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    try {
      await signup({
        email: formData.email,
        password: formData.password,
        software_experience: formData.software_experience,
        hardware_experience: formData.hardware_experience,
        interests: formData.interests,
      });

      // Redirect to chatbot on success
      const redirectUrl = sessionStorage.getItem('auth_redirect') || '/';
      sessionStorage.removeItem('auth_redirect');
      navigate(redirectUrl + '?chatbot=open');
    } catch (error) {
      setErrors({ submit: error.message || 'Signup failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleInterestToggle = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest],
    }));
  };

  const interestOptions = [
    'Robotics',
    'Artificial Intelligence',
    'Machine Learning',
    'Hardware Design',
    'Software Development',
    'IoT',
    'Computer Vision',
    'Natural Language Processing',
    'Autonomous Systems',
    'Embedded Systems',
  ];

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h2>Create Your Account</h2>

      {errors.submit && <div className="auth-error">{errors.submit}</div>}

      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={e => setFormData({...formData, email: e.target.value})}
          placeholder="student@example.com"
          required
        />
        {errors.email && <span className="error-text">{errors.email}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={formData.password}
          onChange={e => setFormData({...formData, password: e.target.value})}
          placeholder="Min 8 characters"
          required
        />
        {errors.password && <span className="error-text">{errors.password}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="confirmPassword">Confirm Password</label>
        <input
          id="confirmPassword"
          type="password"
          value={formData.confirmPassword}
          onChange={e => setFormData({...formData, confirmPassword: e.target.value})}
          placeholder="Re-enter password"
          required
        />
        {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="software">Software Background</label>
        <select
          id="software"
          value={formData.software_experience}
          onChange={e => setFormData({...formData, software_experience: e.target.value})}
          required
        >
          <option value="BEGINNER">Beginner - I'm new to programming</option>
          <option value="INTERMEDIATE">Intermediate - Some programming experience</option>
          <option value="ADVANCED">Advanced - Experienced developer</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="hardware">Hardware Background</label>
        <select
          id="hardware"
          value={formData.hardware_experience}
          onChange={e => setFormData({...formData, hardware_experience: e.target.value})}
          required
        >
          <option value="NONE">No hardware/robotics experience</option>
          <option value="BASIC">Some electronics or maker experience</option>
          <option value="ADVANCED">Experienced with robotics/embedded systems</option>
        </select>
      </div>

      <div className="form-group">
        <label>Interests (Optional)</label>
        <div className="interests-grid">
          {interestOptions.map(interest => (
            <label key={interest} className="interest-checkbox">
              <input
                type="checkbox"
                checked={formData.interests.includes(interest)}
                onChange={() => handleInterestToggle(interest)}
              />
              <span>{interest}</span>
            </label>
          ))}
        </div>
      </div>

      <button type="submit" disabled={loading} className="auth-button">
        {loading ? 'Creating Account...' : 'Sign Up'}
      </button>

      <p className="auth-footer">
        Already have an account? <a href="/auth/signin">Sign In</a>
      </p>
    </form>
  );
}
```

**Purpose**: Signup form with profile data collection

### 1.6 Create Signin Form Component

**File**: `src/components/auth/SigninForm.tsx` (NEW)

```typescript
import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useNavigate } from '@docusaurus/router';
import './auth.css';

export default function SigninForm() {
  const { signin } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await signin(formData.email, formData.password);

      // Redirect to intended page or chatbot
      const redirectUrl = sessionStorage.getItem('auth_redirect') || '/';
      sessionStorage.removeItem('auth_redirect');
      navigate(redirectUrl + '?chatbot=open');
    } catch (error) {
      setError(error.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h2>Sign In</h2>

      {error && <div className="auth-error">{error}</div>}

      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={e => setFormData({...formData, email: e.target.value})}
          placeholder="student@example.com"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={formData.password}
          onChange={e => setFormData({...formData, password: e.target.value})}
          placeholder="Enter your password"
          required
        />
      </div>

      <button type="submit" disabled={loading} className="auth-button">
        {loading ? 'Signing In...' : 'Sign In'}
      </button>

      <p className="auth-footer">
        Don't have an account? <a href="/auth/signup">Sign Up</a>
      </p>
    </form>
  );
}
```

**Purpose**: Signin form for existing users

### 1.7 Create Auth Styles

**File**: `src/components/auth/auth.css` (NEW)

```css
.auth-form {
  max-width: 500px;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--ifm-background-color);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.auth-form h2 {
  margin-bottom: 1.5rem;
  text-align: center;
  color: var(--ifm-color-primary);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--ifm-font-color-base);
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--ifm-color-emphasis-300);
  border-radius: 4px;
  font-size: 1rem;
  background: var(--ifm-background-surface-color);
  color: var(--ifm-font-color-base);
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--ifm-color-primary);
  box-shadow: 0 0 0 3px var(--ifm-color-primary-lightest);
}

.error-text {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: var(--ifm-color-danger);
}

.auth-error {
  padding: 1rem;
  margin-bottom: 1rem;
  background: var(--ifm-color-danger-lightest);
  border-left: 4px solid var(--ifm-color-danger);
  border-radius: 4px;
  color: var(--ifm-color-danger-dark);
}

.interests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.5rem;
}

.interest-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  cursor: pointer;
}

.interest-checkbox input[type="checkbox"] {
  width: auto;
}

.auth-button {
  width: 100%;
  padding: 0.75rem;
  background: var(--ifm-color-primary);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.auth-button:hover:not(:disabled) {
  background: var(--ifm-color-primary-dark);
}

.auth-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-footer {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.875rem;
  color: var(--ifm-font-color-secondary);
}

.auth-footer a {
  color: var(--ifm-color-primary);
  text-decoration: none;
  font-weight: 600;
}

.auth-footer a:hover {
  text-decoration: underline;
}
```

**Purpose**: Styling for auth forms (responsive, theme-aware)

### 1.8 Create Auth Pages

**File**: `src/pages/auth/signup.tsx` (NEW)

```typescript
import React from 'react';
import Layout from '@theme/Layout';
import SignupForm from '@site/src/components/auth/SignupForm';

export default function SignupPage() {
  return (
    <Layout title="Sign Up" description="Create your account">
      <main className="container margin-vert--lg">
        <SignupForm />
      </main>
    </Layout>
  );
}
```

**File**: `src/pages/auth/signin.tsx` (NEW)

```typescript
import React from 'react';
import Layout from '@theme/Layout';
import SigninForm from '@site/src/components/auth/SigninForm';

export default function SigninPage() {
  return (
    <Layout title="Sign In" description="Sign in to your account">
      <main className="container margin-vert--lg">
        <SigninForm />
      </main>
    </Layout>
  );
}
```

**Purpose**: Full pages for signup and signin routes

### 1.9 Create Custom Navbar Item

**File**: `src/theme/NavbarItem/ComponentTypes.tsx` (NEW)

```typescript
import ComponentTypes from '@theme-original/NavbarItem/ComponentTypes';
import CustomLoginLogoutNavbarItem from './CustomLoginLogoutNavbarItem';

export default {
  ...ComponentTypes,
  'custom-LoginLogoutNavbarItem': CustomLoginLogoutNavbarItem,
};
```

**File**: `src/theme/NavbarItem/CustomLoginLogoutNavbarItem.tsx` (NEW)

```typescript
import React from 'react';
import { useAuth } from '@site/src/components/auth/AuthContext';
import { useNavigate } from '@docusaurus/router';

export default function CustomLoginLogoutNavbarItem() {
  const { user, isAuthenticated, isLoading, signout } = useAuth();
  const navigate = useNavigate();

  if (isLoading) {
    return <span className="navbar__item">Loading...</span>;
  }

  if (isAuthenticated && user) {
    return (
      <div className="navbar__item dropdown dropdown--hoverable">
        <button className="navbar__link button button--secondary button--sm">
          {user.email}
        </button>
        <ul className="dropdown__menu">
          <li>
            <a className="dropdown__link" href="/profile">
              Profile
            </a>
          </li>
          <li>
            <button
              className="dropdown__link"
              onClick={async () => {
                await signout();
                navigate('/');
              }}
            >
              Logout
            </button>
          </li>
        </ul>
      </div>
    );
  }

  return (
    <div className="navbar__item">
      <a
        className="navbar__link button button--primary button--sm"
        href="/auth/signin"
      >
        Login
      </a>
    </div>
  );
}
```

**Purpose**: Navbar dropdown showing user email with logout button

### 1.10 Update Docusaurus Config

**File**: `docusaurus.config.ts` (MODIFY)

```typescript
// Add to themeConfig.navbar.items
{
  type: 'custom-LoginLogoutNavbarItem',
  position: 'right',
}
```

**Purpose**: Add login/logout button to navbar

---

## Phase 2: RAG Chatbot Access Gating

### 2.1 Modify Chatbot Widget (Frontend)

**File**: `plugins/rag-chatbot/components/ChatWidget.jsx` (MODIFY)

```javascript
import React, { useState, useEffect } from 'react';
import { useAuth } from '@site/src/components/auth/AuthContext';
import ChatModal from './ChatModal';
import './ChatWidget.css';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, isLoading } = useAuth();

  // Check for chatbot open query param (from auth redirect)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('chatbot') === 'open' && isAuthenticated) {
      setIsOpen(true);
      // Clean up URL
      params.delete('chatbot');
      const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
      window.history.replaceState({}, '', newUrl);
    }
  }, [isAuthenticated]);

  const toggleChat = () => {
    if (!isAuthenticated) {
      // Store current page for redirect after signin
      sessionStorage.setItem('auth_redirect', window.location.pathname);
      window.location.href = '/auth/signin';
      return;
    }

    setIsOpen(!isOpen);
  };

  if (isLoading) {
    return null; // Hide widget while loading auth state
  }

  return (
    <>
      <button
        className="chat-widget-button"
        onClick={toggleChat}
        aria-label="Open chat assistant"
        title={isAuthenticated ? "Ask a question" : "Sign in to use chatbot"}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        {!isOpen && <span className="chat-widget-badge">?</span>}
      </button>

      {isOpen && isAuthenticated && <ChatModal onClose={() => setIsOpen(false)} />}
    </>
  );
}
```

**Purpose**: Enforce auth requirement before opening chatbot

### 2.2 Add Auth to Chatbot API Calls

**File**: `plugins/rag-chatbot/api/client.js` (MODIFY)

```javascript
import { authClient } from '@site/src/lib/auth-client';

const API_URL = window.CHATBOT_API_URL || 'http://localhost:8000';

export async function sendChatMessage(message) {
  const session = await authClient.getSession();

  if (!session?.tokens?.access_token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(`${API_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${session.tokens.access_token}`,
    },
    credentials: 'include',
    body: JSON.stringify({ query: message }),
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired, try refresh
      await authClient.refreshSession();
      // Retry request
      return sendChatMessage(message);
    }
    throw new Error('Failed to send message');
  }

  return response.json();
}
```

**Purpose**: Include auth token in chatbot API requests

### 2.3 Protect Chatbot Endpoint (Backend)

**File**: `backend/src/api/routes/query.py` (MODIFY)

```python
from fastapi import APIRouter, Depends, HTTPException
from src.auth.dependencies import get_current_user
from src.users.models import User

router = APIRouter(prefix="/api", tags=["RAG Chatbot"])

@router.post("/query")
async def query_chatbot(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),  # ← ADD THIS
    db: Session = Depends(get_db),
):
    """
    Process chatbot query with personalization.

    Requires authentication. User profile used for personalization.
    """
    # User is now guaranteed to be authenticated
    user_profile = current_user.profile

    # ... rest of existing code
```

**Purpose**: Enforce authentication on backend

---

## Phase 3: Personalization

### 3.1 Create Personalization Service (Backend)

**File**: `backend/src/services/personalization_service.py` (NEW)

```python
"""
Personalization service for tailoring RAG responses based on user profiles.
"""
from src.users.models import UserProfile, SoftwareExperience, HardwareExperience

def get_personalization_prompt(profile: UserProfile) -> str:
    """
    Generate personalization context for RAG system prompt.

    Args:
        profile: User profile with experience levels and interests

    Returns:
        Prompt text to inject into system prompt
    """
    # Software experience context
    software_context = {
        SoftwareExperience.BEGINNER: "The user is new to programming. Use simple explanations, avoid jargon, and provide step-by-step guidance. Focus on fundamental concepts.",
        SoftwareExperience.INTERMEDIATE: "The user has some programming experience. You can use technical terms but explain complex concepts. Provide practical examples.",
        SoftwareExperience.ADVANCED: "The user is an experienced developer. Use advanced technical language, focus on architecture and best practices. Assume knowledge of fundamentals.",
    }

    # Hardware experience context
    hardware_context = {
        HardwareExperience.NONE: "The user has no hardware/robotics experience. Explain physical concepts from scratch, use analogies, avoid assuming prior knowledge.",
        HardwareExperience.BASIC: "The user has some electronics or maker experience. You can reference basic components and circuits. Explain robotics-specific concepts.",
        HardwareExperience.ADVANCED: "The user is experienced with robotics and embedded systems. Use technical hardware terminology, focus on advanced topics and integration.",
    }

    # Build personalization prompt
    prompt_parts = [
        "## User Background",
        "",
        f"**Software Experience**: {profile.software_experience.value}",
        software_context[profile.software_experience],
        "",
        f"**Hardware Experience**: {profile.hardware_experience.value}",
        hardware_context[profile.hardware_experience],
    ]

    # Add interests if present
    if profile.interests:
        interests_str = ", ".join(profile.interests)
        prompt_parts.extend([
            "",
            f"**Interests**: {interests_str}",
            f"When relevant, relate answers to the user's stated interests: {interests_str}",
        ])

    prompt_parts.extend([
        "",
        "Tailor your response to match the user's experience level. Adjust technical depth, explanation style, and examples accordingly.",
    ])

    return "\n".join(prompt_parts)


def should_recommend_chapter(profile: UserProfile, chapter_level: str, chapter_topics: list[str]) -> bool:
    """
    Determine if a chapter should be recommended based on user profile.

    Args:
        profile: User profile
        chapter_level: "beginner", "intermediate", or "advanced"
        chapter_topics: List of topics covered in chapter (e.g., ["software", "AI", "robotics"])

    Returns:
        True if chapter matches user's level and interests
    """
    # Match software level
    level_match = {
        "beginner": profile.software_experience == SoftwareExperience.BEGINNER,
        "intermediate": profile.software_experience == SoftwareExperience.INTERMEDIATE,
        "advanced": profile.software_experience == SoftwareExperience.ADVANCED,
    }

    if not level_match.get(chapter_level, True):
        return False

    # Check if chapter topics overlap with user interests
    if profile.interests:
        topic_overlap = any(
            interest.lower() in [topic.lower() for topic in chapter_topics]
            for interest in profile.interests
        )
        return topic_overlap

    # Default: recommend all chapters if no interests specified
    return True
```

**Purpose**: Generate personalized context for RAG prompts

### 3.2 Integrate Personalization into RAG Query

**File**: `backend/src/api/routes/query.py` (MODIFY)

```python
from src.services.personalization_service import get_personalization_prompt
from src.users.services import log_chatbot_query

@router.post("/query")
async def query_chatbot(
    request: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process chatbot query with personalization."""

    # Get user profile
    user_profile = current_user.profile

    # Generate personalization context
    personalization_context = get_personalization_prompt(user_profile)

    # Build system prompt with personalization
    system_prompt = f"""{BASE_SYSTEM_PROMPT}

{personalization_context}

Remember to tailor your response based on the user's background above.
"""

    # Call RAG service with personalized prompt
    response = await rag_service.generate_answer(
        query=request.query,
        system_prompt=system_prompt,
        user_id=current_user.id,
    )

    # Log query for analytics
    log_chatbot_query(
        db=db,
        user_id=current_user.id,
        query_text=request.query,
        response_text=response.answer,
        personalization_context={
            "software_experience": user_profile.software_experience.value,
            "hardware_experience": user_profile.hardware_experience.value,
            "interests": user_profile.interests,
        },
    )

    return response
```

**Purpose**: Inject user profile into RAG system prompt

---

## Testing Strategy

### Unit Tests

**Frontend** (`src/__tests__/auth/`):
- `AuthContext.test.tsx` - Auth state management
- `SignupForm.test.tsx` - Form validation
- `SigninForm.test.tsx` - Login flow

**Backend** (`backend/tests/unit/`):
- `test_personalization_service.py` - Prompt generation logic
- `test_auth_routes.py` - Endpoint responses (already exists)

### Integration Tests

**Frontend** (`cypress/e2e/`):
- `auth-flow.cy.ts` - Signup → signin → chatbot access
- `chatbot-gating.cy.ts` - Unauthenticated redirect
- `token-refresh.cy.ts` - Expired token handling

**Backend** (`backend/tests/integration/`):
- `test_auth_integration.py` - Full auth flow with database
- `test_personalized_rag.py` - RAG with different user profiles

---

## Deployment Plan

### Development

1. Apply database migrations (if any new)
2. Start backend: `uvicorn src.main:app --reload --port 8000`
3. Start frontend: `npm start`
4. Test auth flow locally

### Production

**Backend (Railway)**:
1. Ensure `CORS_ORIGINS` includes Vercel URL
2. Verify `DATABASE_URL`, `SECRET_KEY` set
3. Deploy: `git push railway main`

**Frontend (Vercel)**:
1. Set environment variable: `BACKEND_URL=https://your-backend.railway.app`
2. Deploy: `git push origin main` (auto-deploy enabled)
3. Test cross-origin auth

---

## Success Criteria

✅ **Phase 1 Complete** when:
- Users can sign up with profile data
- Users can sign in with email/password
- Login/Logout button appears in navbar
- Auth state persists across page reloads

✅ **Phase 2 Complete** when:
- Unauthenticated users redirected to signin when clicking chatbot
- Authenticated users can access chatbot
- Backend validates auth token on query endpoint
- Redirect flow works (chatbot → signin → chatbot)

✅ **Phase 3 Complete** when:
- Chatbot responses reflect user's software/hardware background
- Beginner users get simplified explanations
- Advanced users get technical depth
- Analytics track personalization effectiveness

---

## Rollback Plan

**If Phase 1 fails**:
- Revert frontend commits
- No backend changes were made
- No data loss

**If Phase 2 fails**:
- Set feature flag `CHATBOT_AUTH_REQUIRED=false`
- Chatbot accessible to all (no auth gating)
- Auth UI remains functional

**If Phase 3 fails**:
- Remove personalization service import
- Use base system prompt (no personalization)
- Chatbot still functional, just generic responses

---

## Next Steps

1. ✅ **Planning Complete**
2. → **Run `/sp.tasks`** to generate task breakdown
3. → **Implement Phase 1** (Frontend Auth UI)
4. → **Implement Phase 2** (Chatbot Gating)
5. → **Implement Phase 3** (Personalization)
6. → **Test & Deploy**

---

**Plan Status**: ✅ READY FOR IMPLEMENTATION

All architectural decisions made, all design artifacts created. Proceed to task generation with `/sp.tasks`.
