import React, { useState } from 'react';
import { useUser } from './UserContext';
import SignupForm from './SignupForm';
import SigninForm from './SigninForm';
import Profile from './Profile';
import styles from './auth.module.css';

// Define the props type
interface LoginLogoutProps {
  showProfileOnLogin?: boolean;
}

const LoginLogout: React.FC<LoginLogoutProps> = ({ showProfileOnLogin = true }) => {
  const { user, isAuthenticated, logout } = useUser();
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
    <div className={styles.authComponent}>
      {isAuthenticated() ? (
        <div className={`${styles.authStatus} ${styles.authenticated}`}>
          <span>{`Welcome, ${user?.email}!`}</span>
          <button
            onClick={() => {
              setAuthMode('profile');
              setShowAuthModal(true);
            }}
            className={styles.profileLink}
          >
            Profile
          </button>
          <button
            onClick={async () => {
              // Use the auth client's signout function to invalidate the session on the backend
              try {
                const { authApi } = await import('../../lib/auth-client');
                await authApi.signout();
              } catch (error) {
                console.error('Error during signout:', error);
              }
              // Then call the local logout function to clear local state
              logout();
            }}
            className={styles.logoutButton}
          >
            Logout
          </button>
        </div>
      ) : (
        <div className={`${styles.authStatus} ${styles.notAuthenticated}`}>
          <button
            onClick={() => setShowAuthModal(true)}
            className={styles.authTrigger}
          >
            Sign In
          </button>
        </div>
      )}

      {/* Modal for authentication forms */}
      {showAuthModal && (
        <div className={styles.authModalOverlay} onClick={closeModal}>
          <div className={styles.authModalContent} onClick={(e) => e.stopPropagation()}>
            {/* Notification */}
            {notification && (
              <div className={`${styles.notification} ${styles[notification.type]}`}>
                {notification.message}
              </div>
            )}

            {/* Mode selector */}
            <div className={styles.authModeSelector}>
              <button
                className={authMode === 'login' ? styles.active : ''}
                onClick={() => setAuthMode('login')}
              >
                Sign In
              </button>
              <button
                className={authMode === 'signup' ? styles.active : ''}
                onClick={() => setAuthMode('signup')}
              >
                Sign Up
              </button>
            </div>

            {/* Form */}
            <div className={styles.authFormContainer}>
              {renderAuthForm()}
            </div>

            {/* Close button */}
            <button className={styles.closeModal} onClick={closeModal}>
              &times;
            </button>
          </div>
        </div>
      )}

      {/* Inline profile display when authenticated */}
      {isAuthenticated() && authMode === 'profile' && showAuthModal && (
        <div className={styles.authModalOverlay} onClick={closeModal}>
          <div className={styles.authModalContent} onClick={(e) => e.stopPropagation()}>
            <Profile
              onProfileUpdated={() => setNotification({ type: 'success', message: 'Profile updated successfully!' })}
              onError={handleAuthError}
            />
            <button className={styles.closeModal} onClick={closeModal}>
              &times;
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoginLogout;