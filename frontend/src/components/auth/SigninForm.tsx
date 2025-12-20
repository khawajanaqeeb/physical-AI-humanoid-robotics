import React, { useState } from 'react';
import { useUser } from './UserContext';

// Define the props type
interface SigninFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
  onForgotPassword?: () => void;
}

const SigninForm: React.FC<SigninFormProps> = ({ onSuccess, onError, onForgotPassword }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useUser(); // Use the context to handle login

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
      // Prepare the signin data
      const signinData = {
        email: formData.email,
        password: formData.password
      };

      // Call the backend signin API
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/v1/auth/signin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(signinData)
      });

      const result = await response.json();

      if (response.ok) {
        // Extract user data and tokens from the response
        const { user_id, email, tokens } = result;

        // Create user profile object (minimal for signin)
        const userProfile = {
          user_id,
          email,
          software_experience: result.software_experience || 'BEGINNER',
          hardware_experience: result.hardware_experience || 'NONE',
          interests: result.interests || [],
          created_at: result.created_at || new Date().toISOString(),
          last_login_at: new Date().toISOString()
        };

        // Login the user (store in context and localStorage)
        login(userProfile, tokens.access_token);

        // Call success callback if provided
        if (onSuccess) {
          onSuccess();
        }
      } else {
        // Handle error response
        const errorMessage = result.detail || result.message || 'Login failed';
        setError(errorMessage);
        if (onError) onError(errorMessage);
      }
    } catch (err) {
      console.error('Signin error:', err);
      setError('Network error. Please try again.');
      if (onError) onError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form signin-form">
      <h2>Sign In</h2>
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            placeholder="your@email.com"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            placeholder="Your password"
          />
        </div>

        <button type="submit" disabled={loading} className="submit-button">
          {loading ? 'Signing In...' : 'Sign In'}
        </button>

        {onForgotPassword && (
          <div className="form-footer">
            <button type="button" onClick={onForgotPassword} className="link-button">
              Forgot Password?
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

export default SigninForm;