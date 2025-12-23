# Quickstart Guide: Authentication System Fix

**Feature**: 008-fix-auth-fetch-error
**Date**: 2025-12-23

## Overview

This guide provides the essential information to implement the fixes for "Failed to fetch" errors in the authentication system. The fixes focus on environment configuration and CORS issues that prevent authentication operations from working in both local and production environments.

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+ with pip
- Docusaurus 3.9.2
- FastAPI 0.104+
- Access to Vercel for deployment configuration

## Environment Setup

### 1. Backend Environment Configuration

**Location**: `backend/.env` (for local development)

```env
# Database Configuration
DATABASE_URL="postgresql://user:password@localhost:5432/your_db"

# JWT Secret
JWT_SECRET_KEY="your-super-secret-jwt-key-here"

# CORS Configuration
ALLOWED_ORIGINS="http://localhost:3000,https://your-vercel-project.vercel.app"

# Environment (development/production)
ENVIRONMENT="development"
```

### 2. Frontend Environment Configuration

**Location**: `.env` (root directory)

```env
# For local development
NEXT_PUBLIC_API_URL=http://localhost:8000

# This will be overridden in Vercel deployment settings
```

### 3. Vercel Environment Variables

In Vercel dashboard → Project Settings → Environment Variables:

```env
NEXT_PUBLIC_API_URL=https://your-project-name.vercel.app/api
```

## Implementation Steps

### Step 1: Fix Backend CORS Configuration

**File**: `backend/src/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# CORS Configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Additional headers for auth
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Authorization"]
)

# Your existing routes...
```

### Step 2: Update Frontend Environment Handling

**File**: `src/lib/auth-client.ts`

Replace the current BACKEND_URL determination:

```typescript
// Updated environment configuration
const getBackendUrl = (): string => {
  // Check for runtime configuration first
  if (typeof window !== 'undefined' && (window as any).__ENV__?.API_URL) {
    return (window as any).__ENV__.API_URL;
  }

  // Check for build-time environment variable
  if (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Fallback to localhost for development
  return 'http://localhost:8000';
};

const BACKEND_URL = getBackendUrl();
```

### Step 3: Add Error Handling Improvements

**File**: `src/lib/auth-client.ts`

Add a custom error class for better error differentiation:

```typescript
export class AuthError extends Error {
  type: 'network' | 'cors' | 'validation' | 'authentication' | 'server';
  statusCode?: number;
  originalError?: any;

  constructor(message: string, type: string, statusCode?: number, originalError?: any) {
    super(message);
    this.name = 'AuthError';
    this.type = type as any;
    this.statusCode = statusCode;
    this.originalError = originalError;
  }
}

// Update the fetch wrapper functions to use better error handling
const makeAuthRequest = async (endpoint: string, options: RequestInit) => {
  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      credentials: 'include',
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || 'Authentication request failed';

      throw new AuthError(
        errorMessage,
        getErrorType(response.status),
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof AuthError) {
      throw error;
    }

    // Network error (failed to fetch)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new AuthError(
        'Unable to connect to authentication server. Please check your internet connection and try again.',
        'network',
        undefined,
        error
      );
    }

    throw new AuthError(
      'Authentication request failed due to an unexpected error',
      'server',
      undefined,
      error
    );
  }
};

// Helper function to determine error type
const getErrorType = (statusCode: number): string => {
  if (statusCode >= 500) return 'server';
  if (statusCode === 401 || statusCode === 403) return 'authentication';
  if (statusCode === 400) return 'validation';
  if (statusCode >= 400) return 'server';
  return 'server';
};
```

### Step 4: Update Docusaurus Configuration

**File**: `docusaurus.config.ts`

Add environment injection for runtime configuration:

```typescript
// Add to the config export
export default config satisfies Config = {
  // ... existing config ...

  clientModules: [
    require.resolve('./src/clientModules/env-injector.ts'),
  ],

  // ... rest of config ...
};
```

**New file**: `src/clientModules/env-injector.ts`

```typescript
// Inject environment variables at runtime
if (typeof window !== 'undefined') {
  (window as any).__ENV__ = {
    API_URL: process.env.NEXT_PUBLIC_API_URL,
  };
}
```

### Step 5: Update Build Configuration

**File**: `docusaurus.config.ts`

Ensure environment variables are available during build:

```typescript
// In the config object, add environment variables
const config: Config = {
  // ... other config ...

  customFields: {
    // Make environment variables available to the build
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },

  // ... rest of config ...
};
```

## Testing the Fix

### 1. Local Testing

1. Start the backend server:
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```

2. Start the Docusaurus frontend:
```bash
npm start
```

3. Test all authentication flows:
   - Signup with a new user
   - Signin with existing user
   - Session persistence after refresh
   - Logout functionality

### 2. Production Testing

1. Deploy backend to production environment
2. Configure Vercel environment variables
3. Deploy frontend to Vercel
4. Test all authentication flows in production

## Common Issues and Solutions

### Issue: "Failed to fetch" in Production Only
**Solution**: Verify Vercel environment variables are set correctly:
- Check NEXT_PUBLIC_API_URL points to your backend
- Ensure CORS configuration allows the production origin

### Issue: CORS Error in Browser Console
**Solution**:
- Verify backend CORS middleware is properly configured
- Check that ALLOWED_ORIGINS includes both local and production URLs

### Issue: Authentication Works Locally but Not in Production
**Solution**:
- Confirm backend URL is correctly configured for production
- Check that authentication endpoints are accessible
- Verify HTTPS is used in production

## Verification Checklist

- [ ] Backend CORS allows both local (http://localhost:3000) and production origins
- [ ] Frontend uses correct environment-specific backend URL
- [ ] Authentication requests include credentials when needed
- [ ] Error messages are user-friendly and specific
- [ ] All auth operations work in local development
- [ ] All auth operations work in production
- [ ] Session state persists correctly after page refresh
- [ ] Logout functionality works properly
- [ ] Protected API calls work with authenticated sessions

## Deployment Notes

1. **Before deploying to Vercel**:
   - Set NEXT_PUBLIC_API_URL environment variable
   - Verify backend is accessible from production environment
   - Test CORS configuration with production URL

2. **Rollback plan**:
   - Keep previous working version available
   - Monitor authentication flows after deployment
   - Have backend access ready for quick fixes if needed