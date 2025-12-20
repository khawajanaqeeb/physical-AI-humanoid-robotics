import React, { useState } from 'react';
import { useUser } from './UserContext';
import SignupForm from './SignupForm';
import SigninForm from './SigninForm';
import Profile from './Profile';

// Define the props type
interface LoginLogoutProps {
  showProfileOnLogin?: boolean;
}

const LoginLogout: React.FC<LoginLogoutProps> = ({ showProfileOnLogin = true }) => {
  const { user, isAuthenticated } = useUser();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'signup' | 'profile'>('login');
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Close modal and reset state
  const closeModal = () => {
    setShowAuthModal(false);
    setTimeout(() => {
      setAuthMode('login');
      setNotification(null);
    }, 300); // Allow for animation transition
  };

  // Handle successful authentication
  const handleAuthSuccess = () => {
    setNotification({ type: 'success', message: 'Authentication successful!' });
    if (!showProfileOnLogin || authMode === 'signup') {
      setTimeout(closeModal, 1500);
    } else {
      setAuthMode('profile');
    }
  };

  // Handle authentication error
  const handleAuthError = (error: string) => {
    setNotification({ type: 'error', message: error });
  };

  // Render appropriate form based on authMode
  const renderAuthForm = () => {
    switch (authMode) {
      case 'signup':
        return (
          <SignupForm
            onSuccess={handleAuthSuccess}
            onError={handleAuthError}
          />
        );
      case 'profile':
        return (
          <Profile
            onProfileUpdated={handleAuthSuccess}
            onError={handleAuthError}
          />
        );
      case 'login':
      default:
        return (
          <SigninForm
            onSuccess={handleAuthSuccess}
            onError={handleAuthError}
            onForgotPassword={() => setAuthMode('signup')} // For now, redirect to signup
          />
        );
    }
  };

  return (
    <div className="auth-component">
      {isAuthenticated() ? (
        <div className="auth-status authenticated">
          <span>Welcome, {user?.email}!</span>
          <button
            onClick={() => {
              setAuthMode('profile');
              setShowAuthModal(true);
            }}
            className="profile-link"
          >
            Profile
          </button>
        </div>
      ) : (
        <div className="auth-status not-authenticated">
          <button
            onClick={() => setShowAuthModal(true)}
            className="auth-trigger"
          >
            Sign In
          </button>
        </div>
      )}

      {/* Modal for authentication forms */}
      {showAuthModal && (
        <div className="auth-modal-overlay" onClick={closeModal}>
          <div className="auth-modal-content" onClick={(e) => e.stopPropagation()}>
            {/* Notification */}
            {notification && (
              <div className={`notification ${notification.type}`}>
                {notification.message}
              </div>
            )}

            {/* Mode selector */}
            <div className="auth-mode-selector">
              <button
                className={authMode === 'login' ? 'active' : ''}
                onClick={() => setAuthMode('login')}
              >
                Sign In
              </button>
              <button
                className={authMode === 'signup' ? 'active' : ''}
                onClick={() => setAuthMode('signup')}
              >
                Sign Up
              </button>
            </div>

            {/* Form */}
            <div className="auth-form-container">
              {renderAuthForm()}
            </div>

            {/* Close button */}
            <button className="close-modal" onClick={closeModal}>
              &times;
            </button>
          </div>
        </div>
      )}

      {/* Inline profile display when authenticated */}
      {isAuthenticated() && authMode === 'profile' && showAuthModal && (
        <div className="auth-modal-overlay" onClick={closeModal}>
          <div className="auth-modal-content" onClick={(e) => e.stopPropagation()}>
            <Profile
              onProfileUpdated={() => setNotification({ type: 'success', message: 'Profile updated successfully!' })}
              onError={handleAuthError}
            />
            <button className="close-modal" onClick={closeModal}>
              &times;
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoginLogout;