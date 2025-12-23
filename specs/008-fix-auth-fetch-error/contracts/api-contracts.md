# API Contracts: Authentication Endpoints

**Feature**: 008-fix-auth-fetch-error
**Date**: 2025-12-23

## Overview

This document defines the API contracts for authentication endpoints that need to be fixed to resolve "Failed to fetch" errors. These contracts specify the expected request/response patterns, CORS requirements, and error handling for authentication operations.

## Base URL

**Local Development**: `http://localhost:8000`
**Production**: Vercel deployment URL (to be configured)

## CORS Configuration Requirements

**Allowed Origins**:
- Local: `http://localhost:3000` (Docusaurus dev server)
- Production: Vercel deployment URL

**Allowed Methods**: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`

**Allowed Headers**: `Content-Type`, `Authorization`, `X-Requested-With`

**Credentials**: `true` (allow cookies/credentials)

**Exposed Headers**: `Content-Length`, `Content-Range`, `Authorization`

## Authentication Endpoints

### 1. User Signup

**Endpoint**: `POST /api/v1/auth/signup`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure_password_123",
  "software_experience": "intermediate",
  "hardware_experience": "beginner",
  "interests": ["AI", "Robotics", "Machine Learning"]
}
```

**Headers**:
- `Content-Type`: `application/json`
- `credentials`: `include` (for cookies if used)

**Response (Success)**:
- Status: `200 OK`
```json
{
  "tokens": {
    "access_token": "jwt_access_token_string",
    "refresh_token": "jwt_refresh_token_string"
  },
  "user": {
    "id": "user_12345",
    "email": "user@example.com",
    "profile": {
      "software_experience": "intermediate",
      "hardware_experience": "beginner",
      "interests": ["AI", "Robotics", "Machine Learning"]
    }
  }
}
```

**Response (Error)**:
- Status: `400 Bad Request` (validation error)
- Status: `409 Conflict` (email already exists)
- Status: `500 Internal Server Error` (server error)

```json
{
  "detail": "Error message explaining the issue"
}
```

### 2. User Signin

**Endpoint**: `POST /api/v1/auth/signin`

**Request**:
```json
{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Headers**:
- `Content-Type`: `application/json`
- `credentials`: `include` (for cookies if used)

**Response (Success)**:
- Status: `200 OK`
```json
{
  "tokens": {
    "access_token": "jwt_access_token_string",
    "refresh_token": "jwt_refresh_token_string"
  },
  "user": {
    "id": "user_12345",
    "email": "user@example.com",
    "profile": {
      "software_experience": "intermediate",
      "hardware_experience": "beginner",
      "interests": ["AI", "Robotics", "Machine Learning"]
    }
  }
}
```

**Response (Error)**:
- Status: `400 Bad Request` (validation error)
- Status: `401 Unauthorized` (invalid credentials)
- Status: `500 Internal Server Error` (server error)

```json
{
  "detail": "Invalid credentials"
}
```

### 3. User Signout

**Endpoint**: `POST /api/v1/auth/signout`

**Request**:
```json
{
  "refresh_token": "jwt_refresh_token_string"
}
```

**Headers**:
- `Content-Type`: `application/json`
- `credentials`: `include` (for cookies if used)

**Response (Success)**:
- Status: `200 OK`
```json
{
  "message": "Successfully signed out"
}
```

**Response (Error)**:
- Status: `400 Bad Request` (validation error)
- Status: `401 Unauthorized` (invalid/missing token)
- Status: `500 Internal Server Error` (server error)

```json
{
  "detail": "Signout failed"
}
```

### 4. Token Refresh

**Endpoint**: `POST /api/v1/auth/refresh`

**Request**:
```json
{
  "refresh_token": "jwt_refresh_token_string"
}
```

**Headers**:
- `Content-Type`: `application/json`
- `credentials`: `include` (for cookies if used)

**Response (Success)**:
- Status: `200 OK`
```json
{
  "access_token": "new_jwt_access_token_string",
  "refresh_token": "new_jwt_refresh_token_string"
}
```

**Response (Error)**:
- Status: `400 Bad Request` (validation error)
- Status: `401 Unauthorized` (invalid/missing refresh token)
- Status: `500 Internal Server Error` (server error)

```json
{
  "detail": "Token refresh failed"
}
```

### 5. Get Profile (Session Check)

**Endpoint**: `GET /api/v1/profile/`

**Headers**:
- `Authorization`: `Bearer jwt_access_token_string`
- `credentials`: `include` (for cookies if used)

**Response (Success)**:
- Status: `200 OK`
```json
{
  "user_id": "user_12345",
  "email": "user@example.com",
  "software_experience": "intermediate",
  "hardware_experience": "beginner",
  "interests": ["AI", "Robotics", "Machine Learning"]
}
```

**Response (Error)**:
- Status: `401 Unauthorized` (invalid/missing access token)
- Status: `500 Internal Server Error` (server error)

```json
{
  "detail": "Authentication required"
}
```

## Error Response Format

All error responses follow this standard format:

```json
{
  "detail": "Human-readable error message",
  "error_code": "optional_error_code",
  "timestamp": "ISO 8601 timestamp"
}
```

## Network Error Handling

**Frontend Error Types**:
- `NetworkError`: Cannot reach the server (DNS, connection refused, timeout)
- `CORS Error`: Cross-origin request blocked by browser
- `AuthenticationError`: 401/403 responses
- `ValidationError`: 400 responses with validation details
- `ServerError`: 5xx responses

**Expected Error Messages**:
- Network errors: "Unable to connect to authentication server"
- CORS errors: "Authentication request blocked by security policy"
- Authentication errors: "Invalid credentials" or "Session expired"
- Server errors: "Authentication service temporarily unavailable"

## Environment-Specific Configuration

**Local Development**:
- Backend URL: `http://localhost:8000`
- Frontend URL: `http://localhost:3000`
- CORS: Allow all origins from local development

**Production**:
- Backend URL: Configured via environment variable
- Frontend URL: Vercel deployment URL
- CORS: Allow only production origin

## Security Requirements

1. **Transport Security**: All endpoints must use HTTPS in production
2. **Token Security**: JWT tokens must be properly signed and validated
3. **Rate Limiting**: Authentication endpoints should have rate limiting
4. **Input Validation**: All inputs must be validated and sanitized
5. **CORS Policy**: Strict origin checking in production