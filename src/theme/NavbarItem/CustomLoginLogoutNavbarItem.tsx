/**
 * Custom Navbar Item for Login/Logout
 * Shows Login button when not authenticated, or user email with logout button when authenticated
 */
import React from 'react';
import { useAuth } from '@site/src/components/auth/AuthContext';
import { useHistory } from '@docusaurus/router';
import '@site/src/components/auth/auth.css';

export default function CustomLoginLogoutNavbarItem() {
  const { user, isAuthenticated, isLoading, signout } = useAuth();
  const history = useHistory();

  const handleLogout = async () => {
    await signout();
    history.push('/');
  };

  if (isLoading) {
    return <span className="navbar__item">Loading...</span>;
  }

  if (isAuthenticated && user) {
    return (
      <div className="navbar__item navbar__item--auth">
        <span className="navbar__link navbar__link--email">
          {user.email}
        </span>
        <button
          className="navbar__link button button--secondary button--sm"
          onClick={handleLogout}
          aria-label={`Logout from ${user.email}`}
        >
          Logout
        </button>
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
