import React, { useState, useEffect } from 'react';
import { useUser } from './UserContext';

// Define the props type
interface ProfileProps {
  onProfileUpdated?: () => void;
  onError?: (error: string) => void;
}

const Profile: React.FC<ProfileProps> = ({ onProfileUpdated, onError }) => {
  const { user, token, updateUserProfile, logout } = useUser();
  const [isLoading, setIsLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    software_experience: user?.software_experience || 'BEGINNER',
    hardware_experience: user?.hardware_experience || 'NONE',
    interests: user?.interests.join(', ') || ''
  });
  const [error, setError] = useState('');

  // Load user profile on component mount
  useEffect(() => {
    if (user) {
      setFormData({
        software_experience: user.software_experience,
        hardware_experience: user.hardware_experience,
        interests: user.interests.join(', ')
      });
      setIsLoading(false);
    } else {
      setIsLoading(false);
    }
  }, [user]);

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
    setUpdating(true);

    try {
      // Prepare interests as array
      const interestsArray = formData.interests
        ? formData.interests.split(',').map(item => item.trim()).filter(item => item)
        : [];

      // Prepare the update data
      const updateData = {
        software_experience: formData.software_experience,
        hardware_experience: formData.hardware_experience,
        interests: interestsArray
      };

      // Call the backend profile update API
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/api/v1/profile/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updateData)
      });

      const result = await response.json();

      if (response.ok) {
        // Update the user profile in context
        updateUserProfile(result);

        // Exit edit mode
        setEditMode(false);

        // Call success callback if provided
        if (onProfileUpdated) {
          onProfileUpdated();
        }
      } else {
        // Handle error response
        const errorMessage = result.detail || result.message || 'Profile update failed';
        setError(errorMessage);
        if (onError) onError(errorMessage);
      }
    } catch (err) {
      console.error('Profile update error:', err);
      setError('Network error. Please try again.');
      if (onError) onError('Network error. Please try again.');
    } finally {
      setUpdating(false);
    }
  };

  // Handle cancel edit
  const handleCancel = () => {
    setEditMode(false);
    if (user) {
      setFormData({
        software_experience: user.software_experience,
        hardware_experience: user.hardware_experience,
        interests: user.interests.join(', ')
      });
    }
  };

  if (isLoading) {
    return <div className="profile-container">Loading profile...</div>;
  }

  if (!user) {
    return (
      <div className="profile-container">
        <p>Please sign in to view your profile.</p>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <h2>Your Profile</h2>

      {error && <div className="error-message">{error}</div>}

      {editMode ? (
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email-display">Email:</label>
            <input
              type="text"
              id="email-display"
              value={user.email}
              readOnly
              disabled
              className="readonly-input"
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

          <div className="form-actions">
            <button type="submit" disabled={updating} className="submit-button">
              {updating ? 'Updating...' : 'Save Changes'}
            </button>
            <button type="button" onClick={handleCancel} className="cancel-button">
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <div className="profile-display">
          <div className="profile-field">
            <strong>Email:</strong> {user.email}
          </div>

          <div className="profile-field">
            <strong>Software Experience:</strong> {user.software_experience}
          </div>

          <div className="profile-field">
            <strong>Hardware/Robotics Experience:</strong> {user.hardware_experience}
          </div>

          <div className="profile-field">
            <strong>Interests:</strong> {user.interests.length > 0 ? user.interests.join(', ') : 'None specified'}
          </div>

          <div className="profile-field">
            <strong>Member Since:</strong> {new Date(user.created_at).toLocaleDateString()}
          </div>

          <div className="profile-actions">
            <button onClick={() => setEditMode(true)} className="edit-button">
              Edit Profile
            </button>

            <button onClick={logout} className="logout-button">
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;