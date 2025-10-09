import React from 'react';
import { TimetableItem } from '../../types/api';

interface DataQualityIndicatorProps {
  item: TimetableItem;
}

const DataQualityIndicator: React.FC<DataQualityIndicatorProps> = ({ item }) => {
  const getDataQuality = (item: TimetableItem) => {
    const requiredFields = ['course', 'time', 'room', 'faculty', 'campus'];
    let validFields = 0;
    let totalFields = requiredFields.length;

    requiredFields.forEach(field => {
      const value = item[field as keyof TimetableItem];
      let isValid = false;
      
      if (value && value !== 'null' && value !== 'undefined' && String(value).trim() !== '') {
        const stringValue = String(value).trim();
        
        // Field-specific validation
        switch (field) {
          case 'room':
            // For room: "-", actual room names, "Lab XX", "Online", etc. are all valid
            isValid = stringValue !== 'TBD';
            break;
          case 'faculty':
            // For faculty: "TBD" is acceptable, any actual name is valid
            isValid = true;
            break;
          case 'time':
            // For time: actual times are valid, "TBD" patterns are partial
            isValid = !stringValue.includes('TBD');
            break;
          case 'campus':
            // For campus: any campus name is valid
            isValid = stringValue !== 'TBD';
            break;
          default:
            // For course and other fields: any non-empty value is valid
            isValid = true;
        }
      }
      
      if (isValid) {
        validFields++;
      }
    });

    const percentage = (validFields / totalFields) * 100;
    
    if (percentage >= 80) return { level: 'excellent', color: 'green', text: 'Complete' };
    if (percentage >= 60) return { level: 'good', color: 'blue', text: 'Good' };
    if (percentage >= 40) return { level: 'fair', color: 'yellow', text: 'Partial' };
    return { level: 'poor', color: 'red', text: 'Incomplete' };
  };

  const quality = getDataQuality(item);

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'green':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'blue':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'yellow':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'red':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <span 
      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getColorClasses(quality.color)}`}
      title={`Data Quality: ${quality.text} (${quality.level})`}
    >
      <span className="w-2 h-2 rounded-full bg-current mr-1"></span>
      {quality.text}
    </span>
  );
};

export default DataQualityIndicator;