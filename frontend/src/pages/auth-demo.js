/**
 * Authentication Demo Page
 *
 * This page demonstrates how to use the authentication components.
 * In a real implementation, you would integrate these components
 * into your existing pages or create links to access them.
 */

import React from 'react';
import Layout from '@theme/Layout';
import { useUser } from '../components/auth/UserContext';
import LoginLogout from '../components/auth/LoginLogout';

export default function AuthDemo() {
  const { user, isAuthenticated } = useUser();

  return (
    <Layout title="Authentication Demo" description="Demonstration of authentication components">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--8 col--offset-2">
            <h1>Authentication Demo</h1>

            <div className="margin-vert--lg">
              <h2>Status</h2>
              {isAuthenticated() ? (
                <div className="alert alert--success">
                  <p><strong>Logged in as:</strong> {user?.email}</p>
                  <p><strong>Software Experience:</strong> {user?.software_experience}</p>
                  <p><strong>Hardware Experience:</strong> {user?.hardware_experience}</p>
                  <p><strong>Interests:</strong> {user?.interests?.join(', ') || 'None specified'}</p>
                </div>
              ) : (
                <div className="alert alert--info">
                  <p>You are not currently logged in.</p>
                </div>
              )}
            </div>

            <div className="margin-vert--lg">
              <h2>Authentication Components</h2>
              <p>Click the button below to access the authentication modal:</p>

              <div style={{ marginTop: '1rem' }}>
                <LoginLogout showProfileOnLogin={true} />
              </div>
            </div>

            <div className="margin-vert--lg">
              <h2>How to Use</h2>
              <ol>
                <li>Click "Sign In" to open the authentication modal</li>
                <li>Choose "Sign Up" to create a new account</li>
                <li>Fill in your email, password, and experience information</li>
                <li>After signing up or logging in, your profile will be displayed above</li>
                <li>Your authentication status will be used to personalize your experience</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}