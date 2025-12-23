import React from 'react';
import Layout from '@theme/Layout';
import SigninForm from '@site/src/components/auth/SigninForm';

export default function SigninPage() {
  return (
    <Layout title="Sign In" description="Sign in to your account">
      <main className="container margin-vert--lg">
        <SigninForm />
      </main>
    </Layout>
  );
}
