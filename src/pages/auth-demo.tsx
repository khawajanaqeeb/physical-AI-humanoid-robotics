import React, { useState } from 'react';
import Layout from '@theme/Layout';
import { useAuth } from '../components/auth/AuthContext';
import SignupForm from '../components/auth/SignupForm';
import SigninForm from '../components/auth/SigninForm';
import '../components/auth/auth.css';

const AuthDemoPage = () => {
  const [isLoginView, setIsLoginView] = useState(true);
  const { user, isAuthenticated } = useAuth();

  const handleSuccess = () => {
    // Redirect or update UI after successful auth
    console.log('Authentication successful');
  };

  const handleError = (error: string) => {
    console.error('Authentication error:', error);
  };

  // If user is already authenticated, show a message
  if (isAuthenticated) {
    return (
      <Layout>
        <div className="auth-container">
          <div className="auth-form">
            <h2>Welcome Back!</h2>
            <p>You are already signed in as {user?.email}</p>
            <div>
              <a href="/">Go to Home</a>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="auth-container">
        <div className="auth-form">
          <h2>
            {isLoginView ? 'Sign In' : 'Create Account'}
          </h2>

          {isLoginView ? (
            <SigninForm onSuccess={handleSuccess} onError={handleError} />
          ) : (
            <SignupForm onSuccess={handleSuccess} onError={handleError} />
          )}

          <div className="auth-footer">
            {isLoginView ? (
              <>
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={() => setIsLoginView(false)}
                  style={{ background: 'none', border: 'none', color: 'var(--ifm-color-primary)', cursor: 'pointer', textDecoration: 'underline' }}
                >
                  Sign Up
                </button>
              </>
            ) : (
              <>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => setIsLoginView(true)}
                  style={{ background: 'none', border: 'none', color: 'var(--ifm-color-primary)', cursor: 'pointer', textDecoration: 'underline' }}
                >
                  Sign In
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AuthDemoPage;