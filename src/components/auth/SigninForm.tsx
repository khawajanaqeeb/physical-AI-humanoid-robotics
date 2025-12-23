import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useUser } from './UserContext';
import { useHistory } from '@docusaurus/router';
import './auth.css';

// Define the props type
interface SigninFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

const SigninForm: React.FC<SigninFormProps> = ({ onSuccess, onError }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { signin } = useAuth();
  const { login } = useUser();
  const history = useHistory();

  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await signin(formData.email, formData.password);

      // Fetch user profile and update UserContext
      const backendUrl = (window as any).CHATBOT_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('access_token');

      if (token) {
        const profileResponse = await fetch(`${backendUrl}/api/v1/profile/`, {
          headers: { 'Authorization': `Bearer ${token}` },
          credentials: 'include',
        });

        if (profileResponse.ok) {
          const profileData = await profileResponse.json();
          login(profileData, token);
        }
      }

      // Redirect to intended page or chatbot
      const redirectUrl = sessionStorage.getItem('auth_redirect') || '/';
      sessionStorage.removeItem('auth_redirect');
      history.push(redirectUrl + '?chatbot=open');

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      const errorMessage = error.message || 'Invalid email or password';
      setError(errorMessage);
      if (onError) onError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h2>Sign In</h2>

      {error && <div className="auth-error">{error}</div>}

      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="student@example.com"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Enter your password"
          required
        />
      </div>

      <button type="submit" disabled={loading} className="auth-button">
        {loading ? 'Signing In...' : 'Sign In'}
      </button>

      <p className="auth-footer">
        Don't have an account? <a href="/auth/signup">Sign Up</a>
      </p>
    </form>
  );
};

export default SigninForm;