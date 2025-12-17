import React from 'react';
import './ProfileDisplay.css';

const ProfileDisplay = ({ profile }) => {
  if (!profile) {
    return null;
  }

  const { company_name, extracted_fields } = profile;

  return (
    <div className="profile-display">
      <h2>🎯 Unified Company Profile: {company_name}</h2>
      
      {/* Business Summary Card */}
      <div className="profile-card summary-card">
        <h3>📊 Business Summary</h3>
        <p>{extracted_fields.business_summary || 'No summary available'}</p>
      </div>

      {/* Structured Fields Grid */}
      <div className="profile-grid">
        {/* Product Lines */}
        <div className="profile-card">
          <h3>🛍️ Product Lines</h3>
          {extracted_fields.product_lines && extracted_fields.product_lines.length > 0 ? (
            <ul>
              {extracted_fields.product_lines.map((product, index) => (
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
          {extracted_fields.target_industries && extracted_fields.target_industries.length > 0 ? (
            <ul>
              {extracted_fields.target_industries.map((industry, index) => (
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
          {extracted_fields.regions && extracted_fields.regions.length > 0 ? (
            <ul>
              {extracted_fields.regions.map((region, index) => (
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
          <p>{extracted_fields.hiring_focus || 'No hiring data available'}</p>
        </div>

        {/* Key Recent Events */}
        <div className="profile-card full-width">
          <h3>📰 Key Recent Events</h3>
          {extracted_fields.key_recent_events && extracted_fields.key_recent_events.length > 0 ? (
            <ul>
              {extracted_fields.key_recent_events.map((event, index) => (
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
