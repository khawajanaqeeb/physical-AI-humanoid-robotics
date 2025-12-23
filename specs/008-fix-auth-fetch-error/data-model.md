# Data Model: Authentication System

**Feature**: 008-fix-auth-fetch-error
**Date**: 2025-12-23

## Overview

This data model defines the entities and structures used in the authentication system that needs to be fixed to resolve "Failed to fetch" errors.

## Entity: User

**Description**: Represents an authenticated user in the system

**Fields**:
- `id` (string): Unique identifier for the user
- `email` (string): User's email address (primary identifier)
- `profile` (object, optional): Additional user profile information
  - `software_experience` (string): User's software development experience level
  - `hardware_experience` (string): User's hardware development experience level
  - `interests` (string[]): Array of user interests

**Validation**:
- `id`: Required, non-empty string
- `email`: Required, valid email format
- `profile.software_experience`: Required, non-empty string
- `profile.hardware_experience`: Required, non-empty string
- `profile.interests`: Optional, array of non-empty strings

## Entity: Session

**Description**: Represents an active user session with authentication tokens

**Fields**:
- `user` (User | null): The user associated with this session, null if not authenticated
- `tokens` (object, optional): Authentication tokens for the session
  - `access_token` (string): JWT access token
  - `refresh_token` (string): JWT refresh token

**Validation**:
- `user`: Optional, must be a valid User object when present
- `tokens.access_token`: Optional, non-empty string when present
- `tokens.refresh_token`: Optional, non-empty string when present

## Entity: SessionState

**Description**: Frontend state representation of the current session

**Fields**:
- `data` (Session | null): Current session data
- `isLoading` (boolean): Whether session data is being loaded

**Validation**:
- `data`: Optional, must be a valid Session object when present
- `isLoading`: Required, boolean value

## Entity: AuthResponse

**Description**: Response structure from authentication API endpoints

**Fields**:
- `tokens` (object): Authentication tokens returned by the API
  - `access_token` (string): JWT access token
  - `refresh_token` (string): JWT refresh token
- `user` (User, optional): User information (may be included in some responses)

**Validation**:
- `tokens.access_token`: Required, non-empty string
- `tokens.refresh_token`: Required, non-empty string
- `user`: Optional, must be a valid User object when present

## Entity: SignupData

**Description**: Input data structure for user signup operations

**Fields**:
- `email` (string): User's email address
- `password` (string): User's password
- `software_experience` (string): User's software experience level
- `hardware_experience` (string): User's hardware experience level
- `interests` (string[], optional): User's interests

**Validation**:
- `email`: Required, valid email format
- `password`: Required, minimum 8 characters
- `software_experience`: Required, non-empty string
- `hardware_experience`: Required, non-empty string
- `interests`: Optional, array of non-empty strings

## Entity: EnvironmentConfig

**Description**: Configuration for different deployment environments

**Fields**:
- `BACKEND_URL` (string): Base URL for the backend API
- `NEXT_PUBLIC_API_URL` (string, optional): Public environment variable for API URL

**Validation**:
- `BACKEND_URL`: Required, valid URL format
- `NEXT_PUBLIC_API_URL`: Optional, valid URL format when present

## Entity: ErrorResponse

**Description**: Standardized error response structure for authentication operations

**Fields**:
- `type` ('network' | 'cors' | 'unauthorized' | 'server'): Type of error that occurred
- `message` (string): User-friendly error message
- `statusCode` (number, optional): HTTP status code if available
- `originalError` (any): Original error object for debugging

**Validation**:
- `type`: Required, must be one of the allowed values
- `message`: Required, non-empty string
- `statusCode`: Optional, valid HTTP status code when present
- `originalError`: Optional, any type

## Relationships

- User → Session (one-to-one): Each user can have one active session
- Session → SessionState (one-to-one): Session data is managed by frontend state
- SignupData → AuthResponse (one-to-one): Signup input produces authentication response
- EnvironmentConfig → AuthResponse (many-to-many): Configuration affects all auth operations

## State Transitions

1. **Unauthenticated State**:
   - `Session.data = null`
   - User not logged in

2. **Authenticating State**:
   - `SessionState.isLoading = true`
   - Authentication request in progress

3. **Authenticated State**:
   - `Session.data.user` populated with User object
   - `Session.data.tokens` contains valid tokens

4. **Session Expired State**:
   - `Session.data.tokens` invalid/expired
   - Automatic redirect to unauthenticated state

## Constraints

- JWT tokens must be stored securely in localStorage (current implementation)
- Session state must be properly managed to prevent race conditions
- Error handling must distinguish between network and authentication errors
- Environment configuration must support both local and production deployments