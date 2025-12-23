/**
 * Login/Logout component for navbar with actual forms
 */
import React, { useState } from 'react';
import { useUser } from './UserContext';
import SignupForm from './SignupForm';
import SigninForm from './SigninForm';

const SimpleLoginLogout = () => {
  const { user, isAuthenticated, logout } = useUser();
  const [showModal, setShowModal] = useState(false);
  const [authMode, setAuthMode] = useState('signin'); // 'signin' or 'signup'

  const handleLogout = async () => {
    // Use the auth client's signout function to invalidate the session on the backend
    try {
      const { authApi } = await import('./../lib/auth-client');
      await authApi.signout();
    } catch (error) {
      console.error('Error during signout:', error);
    }
    // Then call the local logout function to clear local state
    logout();
  };

  const handleAuthSuccess = () => {
    setShowModal(false);
  };

  return (
    <div className="simple-auth-component">
      {isAuthenticated() ? (
        <div className="auth-status auth-status--authenticated">
          <span className="auth-status__welcome">Hi, {user?.email?.split('@')[0]}</span>
          <button
            className="auth-button auth-button--logout"
            onClick={handleLogout}
            title="Sign out"
          >
            Sign Out
          </button>
        </div>
      ) : (
        <button
          className="auth-button auth-button--login"
          onClick={() => setShowModal(true)}
          title="Sign in to personalize your experience"
        >
          Sign In
        </button>
      )}

      {/* Modal with actual auth forms */}
      {showModal && (
        <div className="auth-modal-overlay" onClick={() => setShowModal(false)}>
          <div className="auth-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="auth-modal-header">
              <h3>{authMode === 'signin' ? 'Sign In' : 'Create Account'}</h3>
              <button className="auth-modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>

            <div className="auth-modal-body">
              {authMode === 'signin' ? (
                <SigninForm
                  onSuccess={handleAuthSuccess}
                  onForgotPassword={() => console.log('Forgot password clicked')}
                />
              ) : (
                <SignupForm onSuccess={handleAuthSuccess} />
              )}

              <div className="auth-mode-toggle">
                {authMode === 'signin' ? (
                  <>
                    Don't have an account?{' '}
                    <button
                      type="button"
                      className="switch-mode-link"
                      onClick={() => setAuthMode('signup')}
                    >
                      Sign Up
                    </button>
                  </>
                ) : (
                  <>
                    Already have an account?{' '}
                    <button
                      type="button"
                      className="switch-mode-link"
                      onClick={() => setAuthMode('signin')}
                    >
                      Sign In
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .simple-auth-component {
          display: flex;
          align-items: center;
        }

        .auth-status {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .auth-status__welcome {
          font-size: 0.875rem;
          margin-right: 0.5rem;
        }

        .auth-button {
          padding: 0.375rem 0.75rem;
          border: 1px solid var(--ifm-color-emphasis-300);
          border-radius: var(--ifm-global-radius);
          background-color: transparent;
          color: var(--ifm-color-emphasis-700);
          cursor: pointer;
          font-size: 0.875rem;
          transition: all var(--ifm-transition-fast) var(--ifm-transition-timing-default);
        }

        .auth-button:hover {
          background-color: var(--ifm-color-emphasis-200);
        }

        .auth-button--login {
          background-color: var(--ifm-color-primary);
          color: white;
          border-color: var(--ifm-color-primary);
        }

        .auth-button--login:hover {
          background-color: var(--ifm-color-primary-dark);
          border-color: var(--ifm-color-primary-dark);
        }

        .auth-button--logout {
          background-color: transparent;
          color: var(--ifm-color-danger);
          border-color: var(--ifm-color-danger);
        }

        .auth-button--logout:hover {
          background-color: var(--ifm-color-danger);
          color: white;
        }

        .auth-modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }

        .auth-modal-content {
          background: white;
          border-radius: 8px;
          max-width: 500px;
          width: 90%;
          max-height: 90vh;
          overflow-y: auto;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
          position: relative;
        }

        .auth-modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 1.5rem;
          border-bottom: 1px solid var(--ifm-color-emphasis-200);
        }

        .auth-modal-header h3 {
          margin: 0;
          font-size: 1.25rem;
        }

        .auth-modal-close {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          color: var(--ifm-color-emphasis-500);
          padding: 0;
          width: 30px;
          height: 30px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .auth-modal-close:hover {
          color: var(--ifm-color-emphasis-700);
        }

        .auth-modal-body {
          padding: 1.5rem;
        }

        .auth-mode-toggle {
          margin-top: 1rem;
          font-size: 0.875rem;
          text-align: center;
        }

        .switch-mode-link {
          background: none;
          border: none;
          color: var(--ifm-color-primary);
          text-decoration: underline;
          cursor: pointer;
          padding: 0;
          font-size: inherit;
          margin-left: 0.25rem;
        }

        .switch-mode-link:hover {
          color: var(--ifm-color-primary-dark);
        }
      `}</style>
    </div>
  );
};

export default SimpleLoginLogout;