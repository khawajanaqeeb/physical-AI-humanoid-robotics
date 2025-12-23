import React from 'react';
import Layout from '@theme-original/Layout';

// Simply export the original Layout
// UserProvider is now in Root.tsx
export default function LayoutWrapper(props) {
  return <Layout {...props} />;
}