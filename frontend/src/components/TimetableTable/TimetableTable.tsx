import React from 'react';
import { TimetableItem } from '../../types/api';

interface TimetableTableProps {
  items: TimetableItem[];
}

// Helper function to parse time and convert to minutes for sorting
const parseTimeToMinutes = (timeStr: string): number => {
  if (!timeStr || timeStr === '-') return 0;
  
  // Handle different time formats and extract start time
  // Formats: "08:00 AM - 11:00 AM", "12:00 AM - 02:00 PM", "02:00 PM - 03:30 PM"
  const timeMatch = timeStr.match(/(\d{1,2}):(\d{2})\s*(AM|PM)/i);
  if (!timeMatch) return 0;
  
  let hours = parseInt(timeMatch[1]);
  const minutes = parseInt(timeMatch[2]);
  const period = timeMatch[3].toUpperCase();
  
  // Convert to 24-hour format
  if (period === 'PM' && hours !== 12) {
    hours += 12;
  } else if (period === 'AM' && hours === 12) {
    hours = 0;
  }
  
  const totalMinutes = hours * 60 + minutes;
  
  // Debug logging to help troubleshoot
  console.log(`Time parsing: "${timeStr}" -> ${hours}:${minutes.toString().padStart(2, '0')} (${totalMinutes} minutes)`);
  
  return totalMinutes;
};

// Helper function to group and sort data
const groupAndSortData = (items: TimetableItem[]) => {
  // Group by semester
  const grouped = items.reduce((acc, item) => {
    const semester = item.semester || 'Unknown';
    if (!acc[semester]) {
      acc[semester] = [];
    }
    acc[semester].push(item);
    return acc;
  }, {} as Record<string, TimetableItem[]>);

  // Sort each group by time with better error handling
  Object.keys(grouped).forEach(semester => {
    grouped[semester].sort((a, b) => {
      const timeA = parseTimeToMinutes(a.time || '');
      const timeB = parseTimeToMinutes(b.time || '');
      
      // If times are equal, sort by course code as secondary criteria
      if (timeA === timeB) {
        const courseA = a.course || '';
        const courseB = b.course || '';
        return courseA.localeCompare(courseB);
      }
      
      return timeA - timeB;
    });
    
    // Debug: Log the sorted order for this semester
    console.log(`Semester "${semester}" sorted order:`);
    grouped[semester].forEach((item, index) => {
      const timeMinutes = parseTimeToMinutes(item.time || '');
      console.log(`  ${index + 1}. ${item.course} - ${item.time} (${timeMinutes} minutes)`);
    });
  });

  // Sort semesters alphabetically
  const sortedSemesters = Object.keys(grouped).sort();
  
  return { grouped, sortedSemesters };
};

const TimetableTable: React.FC<TimetableTableProps> = ({ items }) => {
  const { grouped, sortedSemesters } = groupAndSortData(items);

  if (!items || items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No timetable data available
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Course
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider max-w-xs">
              Course Title
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Faculty
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Room
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Time
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Semester
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Campus
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sortedSemesters.map((semester, semesterIndex) => (
            <React.Fragment key={semester}>
              {/* Semester Header Row */}
              <tr className="bg-blue-50 border-t-2 border-blue-200">
                <td colSpan={7} className="px-6 py-4 text-sm font-semibold text-blue-800 bg-blue-100">
                  <div className="flex items-center">
                    <span className="mr-2">🏛️</span>
                    {semester} ({grouped[semester].length} classes)
                  </div>
                </td>
              </tr>
              {/* Classes for this semester */}
              {grouped[semester].map((item, itemIndex) => (
                <tr key={`${semester}-${itemIndex}`} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.course || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs">
                    <div className="break-words leading-5">
                      {item.course_title || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.faculty || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.room || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.time || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.semester || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.campus || '-'}
                  </td>
                </tr>
              ))}
            </React.Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TimetableTable;