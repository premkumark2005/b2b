import React from 'react';
import './ConfidenceBar.css';

const ConfidenceBar = ({ value }) => {
  // Convert 0-1 to 0-100 percentage
  const percentage = Math.round(value * 100);
  
  // Determine confidence level and color
  let level = 'low';
  let color = '#ef4444'; // red
  
  if (value >= 0.75) {
    level = 'high';
    color = '#22c55e'; // green
  } else if (value >= 0.4) {
    level = 'medium';
    color = '#f59e0b'; // orange
  }
  
  return (
    <div className="confidence-container">
      <div className="confidence-bar-wrapper">
        <div 
          className="confidence-bar-fill" 
          style={{ width: `${percentage}%`, backgroundColor: color }}
        >
          <span className="confidence-percentage">{percentage}%</span>
        </div>
      </div>
      <span className={`confidence-badge confidence-${level}`}>
        {level === 'high' && '✓ High Confidence'}
        {level === 'medium' && '~ Medium Confidence'}
        {level === 'low' && '! Low Confidence'}
      </span>
    </div>
  );
};

export default ConfidenceBar;
