import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { useUser } from './UserContext';
import { useHistory } from '@docusaurus/router';
import './auth.css';

// Predefined interests options (10 options as per spec FR-001a)
const PREDEFINED_INTERESTS = [
  'Robotics',
  'Artificial Intelligence',
  'Machine Learning',
  'Hardware Design',
  'Software Development',
  'IoT',
  'Computer Vision',
  'Natural Language Processing',
  'Autonomous Systems',
  'Embedded Systems'
] as const;

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
    interests: [] as string[] // Array of selected interests
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { signup } = useAuth();
  const { login } = useUser();
  const history = useHistory();

  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle interest checkbox changes
  const handleInterestToggle = (interest: string) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  // Validation function
  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-zA-Z])(?=.*[0-9])/.test(formData.password)) {
      newErrors.password = 'Password must contain letters and numbers';
    }

    // Confirm password
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords must match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    try {
      await signup({
        email: formData.email,
        password: formData.password,
        software_experience: formData.software_experience,
        hardware_experience: formData.hardware_experience,
        interests: formData.interests,
      });

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

      // Redirect to chatbot on success
      const redirectUrl = sessionStorage.getItem('auth_redirect') || '/';
      sessionStorage.removeItem('auth_redirect');
      history.push(redirectUrl + '?chatbot=open');

      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      const errorMessage = error.message || 'Signup failed. Please try again.';
      setErrors({ submit: errorMessage });
      if (onError) onError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={handleSubmit}>
      <h2>Create Your Account</h2>

      {errors.submit && <div className="auth-error">{errors.submit}</div>}

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
        {errors.email && <span className="error-text">{errors.email}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="Min 8 characters"
          required
        />
        {errors.password && <span className="error-text">{errors.password}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="confirmPassword">Confirm Password</label>
        <input
          id="confirmPassword"
          type="password"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          placeholder="Re-enter password"
          required
        />
        {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="software_experience">Software Background</label>
        <select
          id="software_experience"
          name="software_experience"
          value={formData.software_experience}
          onChange={handleChange}
          required
        >
          <option value="BEGINNER">Beginner - I'm new to programming</option>
          <option value="INTERMEDIATE">Intermediate - Some programming experience</option>
          <option value="ADVANCED">Advanced - Experienced developer</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="hardware_experience">Hardware Background</label>
        <select
          id="hardware_experience"
          name="hardware_experience"
          value={formData.hardware_experience}
          onChange={handleChange}
          required
        >
          <option value="NONE">No hardware/robotics experience</option>
          <option value="BASIC">Some electronics or maker experience</option>
          <option value="ADVANCED">Experienced with robotics/embedded systems</option>
        </select>
      </div>

      <div className="form-group">
        <label>Interests (Optional)</label>
        <div className="interests-grid">
          {PREDEFINED_INTERESTS.map((interest) => (
            <label key={interest} className="interest-checkbox">
              <input
                type="checkbox"
                checked={formData.interests.includes(interest)}
                onChange={() => handleInterestToggle(interest)}
              />
              <span>{interest}</span>
            </label>
          ))}
        </div>
      </div>

      <button type="submit" disabled={loading} className="auth-button">
        {loading ? 'Creating Account...' : 'Sign Up'}
      </button>

      <p className="auth-footer">
        Already have an account? <a href="/auth/signin">Sign In</a>
      </p>
    </form>
  );
};

export default SignupForm;