import React from 'react';
import './ProfileDisplay.css';
import ConfidenceBar from './ConfidenceBar';

const ProfileDisplay = ({ profile }) => {
  if (!profile) {
    return null;
  }

  const { company_name, profile: profileData } = profile;

  return (
    <div className="profile-display">
      <h2>🎯 Unified Company Profile: {company_name}</h2>
      
      {/* Business Summary Card */}
      <div className="profile-card summary-card">
        <h3>📊 Business Summary</h3>
        <ConfidenceBar value={profileData.business_summary.confidence} />
        <p>{profileData.business_summary.value || 'No summary available'}</p>
      </div>

      {/* Structured Fields Grid */}
      <div className="profile-grid">
        {/* Product Lines */}
        <div className="profile-card">
          <h3>🛍️ Product Lines</h3>
          <ConfidenceBar value={profileData.product_lines.confidence} />
          {profileData.product_lines.value && profileData.product_lines.value.length > 0 ? (
            <ul>
              {profileData.product_lines.value.map((product, index) => (
                <li key={index}>{product}</li>
              ))}
            </ul>
          ) : (
            <p className="no-data">No product data</p>
          )}
        </div>

        {/* Target Industries */}
        <div className="profile-card">
          <h3>🏭 Target Industries</h3>
          <ConfidenceBar value={profileData.target_industries.confidence} />
          {profileData.target_industries.value && profileData.target_industries.value.length > 0 ? (
            <ul>
              {profileData.target_industries.value.map((industry, index) => (
                <li key={index}>{industry}</li>
              ))}
            </ul>
          ) : (
            <p className="no-data">No industry data</p>
          )}
        </div>

        {/* Regions */}
        <div className="profile-card">
          <h3>🌍 Regions</h3>
          <ConfidenceBar value={profileData.regions.confidence} />
          {profileData.regions.value && profileData.regions.value.length > 0 ? (
            <ul>
              {profileData.regions.value.map((region, index) => (
                <li key={index}>{region}</li>
              ))}
            </ul>
          ) : (
            <p className="no-data">No region data</p>
          )}
        </div>

        {/* Hiring Focus */}
        <div className="profile-card">
          <h3>💼 Hiring Focus</h3>
          <ConfidenceBar value={profileData.hiring_focus.confidence} />
          {profileData.hiring_focus.value && profileData.hiring_focus.value.length > 0 ? (
            <ul>
              {profileData.hiring_focus.value.map((role, index) => (
                <li key={index}>{role}</li>
              ))}
            </ul>
          ) : (
            <p className="no-data">No hiring data available</p>
          )}
        </div>

        {/* Key Recent Events */}
        <div className="profile-card full-width">
          <h3>📰 Key Recent Events</h3>
          <ConfidenceBar value={profileData.key_recent_events.confidence} />
          {profileData.key_recent_events.value && profileData.key_recent_events.value.length > 0 ? (
            <ul>
              {profileData.key_recent_events.value.map((event, index) => (
                <li key={index}>{event}</li>
              ))}
            </ul>
          ) : (
            <p className="no-data">No recent events</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileDisplay;
