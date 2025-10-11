import React from 'react';
import { motion } from 'framer-motion';
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
  
  // Prepare semester breakdown with missing semesters highlighted
  let semesterBadges: React.ReactNode[] = [];
  const semesterBreakdown = displaySummary.semester_breakdown || {};
  const configuredSemesters = config?.semester_filter || [];
  const foundSemesters = Object.keys(semesterBreakdown);

  // Show all configured semesters, highlight missing ones in red
  // Helper to normalize semester names (trim and remove spaces/dashes)
  const normalizeSemester = (s: string) => s.replace(/\s|-/g, '').toLowerCase();

  if (configuredSemesters.length > 0) {
    semesterBadges = configuredSemesters.map((semester) => {
      const normalizedSemester = normalizeSemester(semester);
      // Find matching key in breakdown
      const foundKey = Object.keys(semesterBreakdown).find(
        key => normalizeSemester(key) === normalizedSemester
      );
      if (foundKey) {
        const count = semesterBreakdown[foundKey];
        return (
          <span key={semester} className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-200 shadow-sm hover:bg-blue-100">
            {semester}
            <span className="ml-2 bg-blue-200 text-blue-900 rounded-full px-2 py-0.5 text-xs font-bold">{count}</span>
          </span>
        );
      } else {
        // Missing semester, highlight red
        return (
          <span key={semester} className="inline-flex items-center px-3 py-1 rounded-full bg-red-50 text-red-700 text-xs font-semibold border border-red-200 shadow-sm hover:bg-red-100">
            {semester}
            <span className="ml-2 bg-red-200 text-red-900 rounded-full px-2 py-0.5 text-xs font-bold">Missing</span>
          </span>
        );
      }
    });
  } else {
    // No filter, show all found semesters
    semesterBadges = Object.entries(semesterBreakdown).map(([semester, count]) => (
      <span key={semester} className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-200 shadow-sm hover:bg-blue-100">
        {semester}
        <span className="ml-2 bg-blue-200 text-blue-900 rounded-full px-2 py-0.5 text-xs font-bold">{count}</span>
      </span>
    ));
  }

  return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <motion.div
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3 }}
          className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg hover:scale-105"
        >
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <img src="/courses.svg" alt="Total Classes" className="w-8 h-8" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Classes</dt>
                  <dd className="text-lg font-medium text-gray-900">{displaySummary.total_items || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.05 }}
          className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg hover:scale-105"
        >
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <img src="/uniqueCourses.svg" alt="Unique Courses" className="w-8 h-8" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Unique Courses</dt>
                  <dd className="text-lg font-medium text-gray-900">{displaySummary.unique_courses || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.1 }}
          className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg hover:scale-105"
        >
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <img src="/faculty.svg" alt="Faculty Members" className="w-8 h-8" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Faculty Members</dt>
                  <dd className="text-lg font-medium text-gray-900">{displaySummary.unique_faculty || 0}</dd>
                </dl>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.15 }}
          className="bg-white overflow-hidden shadow rounded-lg hover:shadow-lg hover:scale-105"
        >
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <img src="/day.svg" alt="Day" className="w-8 h-8" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Day</dt>
                  <dd className="text-lg font-medium text-gray-900">{data.for_day || 'Unknown'}</dd>
                </dl>
              </div>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.2 }}
          className="bg-white overflow-hidden shadow rounded-lg col-span-1 md:col-span-2 lg:col-span-4"
        >
          <div className="p-5">
            <div className="flex items-center mb-2">
              <span className="font-semibold text-gray-700 text-base">Semester Breakdown</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {semesterBadges.length > 0 ? (
                semesterBadges
              ) : (
                <span className="text-gray-400 text-xs">No semester data available</span>
              )}
            </div>
          </div>
        </motion.div>
      </div>
  );
};

export default SummaryStats;