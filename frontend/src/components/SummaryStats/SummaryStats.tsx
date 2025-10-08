import React from 'react';
import { TimetableData, ConfigData } from '../../types/api';

interface SummaryStatsProps {
  data: TimetableData;
  config?: ConfigData;
}

const SummaryStats: React.FC<SummaryStatsProps> = ({ data, config }) => {
  if (!data || !data.summary) {
    return null;
  }

  const summary = data.summary;
  
  // Check if no semesters are configured
  const noSemestersConfigured = !config?.semester_filter || config.semester_filter.length === 0;
  
  // If no semesters configured, show zeros for all stats
  const displaySummary = noSemestersConfigured ? {
    total_items: 0,
    unique_courses: 0,
    unique_faculty: 0,
    semester_breakdown: {}
  } : summary;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <img src="/courses.svg" alt="Total Classes" className="w-8 h-8" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Total Classes
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {displaySummary.total_items || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <img src="/uniqueCourses.svg" alt="Unique Courses" className="w-8 h-8" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Unique Courses
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {displaySummary.unique_courses || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <img src="/faculty.svg" alt="Faculty Members" className="w-8 h-8" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Faculty Members
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {displaySummary.unique_faculty || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="p-5">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <img src="/day.svg" alt="Day" className="w-8 h-8" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Day
                </dt>
                <dd className="text-lg font-medium text-gray-900">
                  {data.for_day || 'Unknown'}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white overflow-hidden shadow rounded-lg col-span-1 md:col-span-2 lg:col-span-4">
        <div className="p-5">
          <div className="flex items-center mb-2">
            <span className="font-semibold text-gray-700 text-base">Semester Breakdown</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(displaySummary.semester_breakdown).length > 0 ? (
              Object.entries(displaySummary.semester_breakdown).map(([semester, count]) => (
                <span key={semester} className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-200 shadow-sm">
                  {semester}
                  <span className="ml-2 bg-blue-200 text-blue-900 rounded-full px-2 py-0.5 text-xs font-bold">{count}</span>
                </span>
              ))
            ) : (
              <span className="text-gray-400 text-xs">No semester data available</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummaryStats;