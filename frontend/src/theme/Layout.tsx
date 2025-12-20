import React from 'react';
import { UserProvider } from '../components/auth/UserContext';
import Layout from '@theme-original/Layout';

// Create a wrapper component that provides the authentication context
const AuthLayout = (props) => {
  return (
    <UserProvider>
      <Layout {...props} />
    </UserProvider>
  );
};

export default AuthLayout;