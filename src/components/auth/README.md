# Authentication Components

This directory contains React components for user authentication and profile management.

## Components

### `UserContext`
- Global authentication state management
- Stores user profile and authentication tokens
- Provides `useUser` hook for accessing user data

### `SignupForm`
- Registration form with email, password, and experience level fields
- Validates password strength and email format
- Submits to backend `/api/v1/auth/signup` endpoint

### `SigninForm`
- Login form with email and password fields
- Authenticates with backend `/api/v1/auth/signin` endpoint
- Stores authentication tokens in localStorage

### `Profile`
- Displays and allows editing of user profile information
- Shows current experience levels and interests
- Updates profile via backend `/api/v1/profile/` endpoint

### `LoginLogout`
- Unified component for authentication flows
- Shows login/signup forms in a modal
- Displays user profile when authenticated

## Environment Variables

Add to your `.env` file:
```
BACKEND_URL=http://localhost:8000
```

## Usage

### Wrap your app with UserProvider:
```jsx
import { UserProvider } from './components/auth';

function App() {
  return (
    <UserProvider>
      {/* Your app content */}
    </UserProvider>
  );
}
```

### Use the authentication components:
```jsx
import { LoginLogout, useUser } from './components/auth';

// In your component
function MyComponent() {
  const { user, isAuthenticated } = useUser();

  return (
    <div>
      {isAuthenticated() ? (
        <p>Welcome, {user.email}!</p>
      ) : (
        <LoginLogout />
      )}
    </div>
  );
}
```

## Integration with RAG Chatbot

The authentication system is automatically integrated with the RAG chatbot. When a user is authenticated, their access token is included in all query requests to enable personalized responses based on their experience level and interests.