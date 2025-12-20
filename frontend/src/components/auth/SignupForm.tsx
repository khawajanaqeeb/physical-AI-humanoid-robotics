import React, { useState } from 'react';
import { useUser } from './UserContext';

// Define the props type
interface SignupFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

const SignupForm: React.FC<SignupFormProps> = ({ onSuccess, onError }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    software_experience: 'BEGINNER',
    hardware_experience: 'NONE',
    interests: '' // Will be converted to array
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useUser(); // Use the context to handle login after signup

  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
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

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      if (onError) onError('Passwords do not match');
      return;
    }

    // Validate password strength
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      if (onError) onError('Password must be at least 8 characters long');
      return;
    }

    // Check for at least one letter and one number in password
    const hasLetter = /[a-zA-Z]/.test(formData.password);
    const hasNumber = /\d/.test(formData.password);
    if (!hasLetter || !hasNumber) {
      setError('Password must contain at least one letter and one number');
      if (onError) onError('Password must contain at least one letter and one number');
      return;
    }

    setLoading(true);

    try {
      // Prepare interests as array
      const interestsArray = formData.interests
        ? formData.interests.split(',').map(item => item.trim()).filter(item => item)
        : [];

      // Prepare the signup data
      const signupData = {
        email: formData.email,
        password: formData.password,
        software_experience: formData.software_experience,
        hardware_experience: formData.hardware_experience,
        interests: interestsArray
      };

      // Call the backend signup API
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/v1/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(signupData)
      });

      const result = await response.json();

      if (response.ok) {
        // Extract user data and tokens from the response
        const { user_id, email, tokens } = result;

        // Create user profile object
        const userProfile = {
          user_id,
          email,
          software_experience: formData.software_experience,
          hardware_experience: formData.hardware_experience,
          interests: interestsArray,
          created_at: new Date().toISOString(),
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
        const errorMessage = result.detail || result.message || 'Signup failed';
        setError(errorMessage);
        if (onError) onError(errorMessage);
      }
    } catch (err) {
      console.error('Signup error:', err);
      setError('Network error. Please try again.');
      if (onError) onError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form signup-form">
      <h2>Create Account</h2>
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
            minLength={8}
            placeholder="At least 8 characters with letters and numbers"
          />
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password:</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            placeholder="Same as password above"
          />
        </div>

        <div className="form-group">
          <label htmlFor="software_experience">Software Experience:</label>
          <select
            id="software_experience"
            name="software_experience"
            value={formData.software_experience}
            onChange={handleChange}
          >
            <option value="BEGINNER">Beginner</option>
            <option value="INTERMEDIATE">Intermediate</option>
            <option value="ADVANCED">Advanced</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="hardware_experience">Hardware/Robotics Experience:</label>
          <select
            id="hardware_experience"
            name="hardware_experience"
            value={formData.hardware_experience}
            onChange={handleChange}
          >
            <option value="NONE">None</option>
            <option value="BASIC">Basic</option>
            <option value="ADVANCED">Advanced</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="interests">Interests (comma separated):</label>
          <input
            type="text"
            id="interests"
            name="interests"
            value={formData.interests}
            onChange={handleChange}
            placeholder="e.g., robotics, AI, computer vision"
          />
        </div>

        <button type="submit" disabled={loading} className="submit-button">
          {loading ? 'Creating Account...' : 'Sign Up'}
        </button>
      </form>
    </div>
  );
};

export default SignupForm;