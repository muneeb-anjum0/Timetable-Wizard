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
      <div className="bg-gradient-to-br from-white to-slate-50/50 overflow-hidden shadow-md rounded-xl border border-slate-200/50 transition-all duration-300 hover:shadow-lg hover:scale-105 animate-drop-bounce delay-150 enhanced-hover">
        <div className="p-4 relative">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-slate-100 p-2 rounded-xl border border-slate-200">
              <img src="/courses.svg" alt="Total Classes" className="w-5 h-5 text-slate-600" />
            </div>
            <div className="ml-4 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-slate-600 truncate">
                  Total Classes
                </dt>
                <dd className="text-2xl font-bold text-slate-800 mt-1">
                  {displaySummary.total_items || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-white to-blue-50/50 overflow-hidden shadow-md rounded-xl border border-blue-200/50 transition-all duration-300 hover:shadow-lg hover:scale-105 animate-drop-bounce delay-200 enhanced-hover">
        <div className="p-4 relative">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-blue-100 p-2 rounded-xl border border-blue-200">
              <img src="/uniqueCourses.svg" alt="Unique Courses" className="w-5 h-5 text-blue-600" />
            </div>
            <div className="ml-4 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-blue-700 truncate">
                  Unique Courses
                </dt>
                <dd className="text-2xl font-bold text-blue-800 mt-1">
                  {displaySummary.unique_courses || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-white to-gray-50/50 overflow-hidden shadow-md rounded-xl border border-gray-200/50 transition-all duration-300 hover:shadow-lg hover:scale-105 animate-drop-bounce delay-250 enhanced-hover">
        <div className="p-4 relative">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-gray-100 p-2 rounded-xl border border-gray-200">
              <img src="/faculty.svg" alt="Faculty Members" className="w-5 h-5 text-gray-600" />
            </div>
            <div className="ml-4 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-700 truncate">
                  Faculty Members
                </dt>
                <dd className="text-2xl font-bold text-gray-800 mt-1">
                  {displaySummary.unique_faculty || 0}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-white to-slate-50/50 overflow-hidden shadow-md rounded-xl border border-slate-200/50 transition-all duration-300 hover:shadow-lg hover:scale-105 animate-drop-bounce delay-300 enhanced-hover">
        <div className="p-4 relative">
          <div className="flex items-center">
            <div className="flex-shrink-0 bg-slate-100 p-2 rounded-xl border border-slate-200">
              <img src="/day.svg" alt="Day" className="w-5 h-5 text-slate-600" />
            </div>
            <div className="ml-4 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-slate-700 truncate">
                  Current Day
                </dt>
                <dd className="text-xl font-bold text-slate-800 mt-1">
                  {data.for_day || 'Today'}
                </dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-white to-slate-50/50 overflow-hidden shadow-md rounded-xl border border-slate-200/50 col-span-1 md:col-span-2 lg:col-span-4 transition-all duration-300 hover:shadow-lg hover:scale-105 animate-drop-bounce delay-350 enhanced-hover">
        <div className="p-4 relative">
          <div className="flex items-center mb-4">
            <div className="bg-slate-100 p-2 rounded-xl border border-slate-200 mr-3">
              <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <span className="font-bold text-slate-800 text-lg">Semester Breakdown</span>
          </div>
          <div className="flex flex-wrap gap-3">
            {Object.entries(displaySummary.semester_breakdown).length > 0 ? (
              Object.entries(displaySummary.semester_breakdown).map(([semester, count], index) => (
                <span key={semester} className="inline-flex items-center px-4 py-2 rounded-xl bg-gradient-to-r from-slate-50 to-slate-100 text-slate-700 text-sm font-semibold border border-slate-300 shadow-sm transition-all duration-300 hover:shadow-md hover:scale-105 enhanced-hover animate-drop-subtle" style={{animationDelay: `${400 + index * 50}ms`}}>
                  <span className="mr-2">{semester}</span>
                  <span className="bg-gradient-to-r from-slate-600 to-slate-700 text-white rounded-full px-2.5 py-1 text-xs font-bold shadow-sm">{count}</span>
                </span>
              ))
            ) : (
              <span className="text-slate-500 text-sm bg-slate-100 px-4 py-2 rounded-xl border border-slate-200">No semester data available</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SummaryStats;