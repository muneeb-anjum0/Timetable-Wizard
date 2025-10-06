import React, { useState, useEffect } from 'react';
import { RefreshCw, Calendar, Settings, Activity } from 'lucide-react';
import './App.css';
import { apiService } from './services/api';
import { TimetableData, ApiResponse, StatusData, ConfigData } from './types/api';
import TimetableTable from './components/TimetableTable/TimetableTable';
import SummaryStats from './components/SummaryStats/SummaryStats';
import StatusIndicator from './components/StatusIndicator/StatusIndicator';
import SemesterManager from './components/SemesterManager/SemesterManager';

function App() {
  const [timetableData, setTimetableData] = useState<TimetableData | null>(null);
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error' | 'warning'>('idle');
  const [message, setMessage] = useState('');
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);
  const [showSemesterManager, setShowSemesterManager] = useState(false);

  // Load initial data on component mount
  useEffect(() => {
    loadLatestTimetable();
    loadConfig();
    checkStatus();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await apiService.getConfig();
      console.log('Config response:', response); // Debug log
      if (response.success && response.data) {
        setConfig(response.data);
        console.log('Loaded config:', response.data); // Debug log
      } else {
        console.error('Failed to load config:', response);
      }
    } catch (error) {
      console.error('Error loading config:', error);
    }
  };

  const loadLatestTimetable = async () => {
    try {
      setIsLoading(true);
      const response = await apiService.getLatestTimetable();
      if (response.success && response.data) {
        setTimetableData(response.data);
        setStatus('success');
        setMessage(response.cached ? 'Loaded cached data' : 'Data loaded successfully');
      } else {
        setStatus('warning');
        setMessage('No timetable data available. Try running a manual scrape.');
      }
    } catch (error) {
      setStatus('error');
      setMessage('Failed to load timetable data');
      console.error('Error loading timetable:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const checkStatus = async () => {
    try {
      const response: ApiResponse<StatusData> = await apiService.getStatus();
      if (response.success && response.data) {
        setLastUpdate(response.data.last_update);
      }
    } catch (error) {
      console.error('Error checking status:', error);
    }
  };

  const runScraper = async () => {
    try {
      setIsLoading(true);
      setStatus('loading');
      setMessage('Running scraper...');
      
      const response = await apiService.runScraper();
      if (response.success && response.data) {
        setTimetableData(response.data);
        setStatus('success');
        setMessage(response.message || 'Scrape completed successfully');
        await checkStatus(); // Update last update time
      } else {
        setStatus('error');
        setMessage(response.error || 'Scrape failed');
      }
    } catch (error) {
      setStatus('error');
      setMessage('Failed to run scraper');
      console.error('Error running scraper:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveSemesters = async (newSemesters: string[]) => {
    try {
      setIsLoading(true);
      const response = await apiService.updateSemesters(newSemesters);
      if (response.success) {
        // Reload config to get updated data
        await loadConfig();
        setStatus('success');
        setMessage(`Successfully updated ${newSemesters.length} allowed semesters`);
      } else {
        setStatus('error');
        setMessage(response.error || 'Failed to update semesters');
      }
    } catch (error) {
      setStatus('error');
      setMessage('Failed to update semesters');
      console.error('Error updating semesters:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatLastUpdate = (timestamp: string | null) => {
    if (!timestamp) return 'Never';
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return 'Unknown';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Calendar className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">TimeTable Scraper</h1>
                <p className="text-sm text-gray-500">University Class Schedule Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Last updated: {formatLastUpdate(lastUpdate)}
              </div>
              <button
                onClick={() => setShowSemesterManager(true)}
                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Settings className="h-4 w-4 mr-2" />
                Semesters ({config?.semester_filter?.length || 0})
              </button>
              <button
                onClick={runScraper}
                disabled={isLoading}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                {isLoading ? 'Scraping...' : 'Run Scraper'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {/* Status Indicator */}
          {message && (
            <div className="mb-6">
              <StatusIndicator 
                status={status === 'loading' ? 'loading' : status === 'success' ? 'success' : status === 'warning' ? 'warning' : 'error'} 
                message={message} 
              />
            </div>
          )}

          {/* Summary Stats */}
          {timetableData && (
            <div className="mb-8">
              <SummaryStats data={timetableData} />
            </div>
          )}

          {/* Timetable */}
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg leading-6 font-medium text-gray-900">
                    Class Schedule
                  </h3>
                  <p className="mt-1 max-w-2xl text-sm text-gray-500">
                    {timetableData 
                      ? `${timetableData.for_day} - ${new Date(timetableData.for_date).toLocaleDateString()}`
                      : 'No data available'
                    }
                  </p>
                </div>
                <div className="flex items-center">
                  <Activity className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm text-gray-500">
                    {timetableData?.items?.length || 0} classes
                  </span>
                </div>
              </div>
            </div>
            
            <div className="px-4 py-5 sm:p-6">
              {timetableData ? (
                <TimetableTable items={timetableData.items} />
              ) : (
                <div className="text-center py-12">
                  <Calendar className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No schedule data</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Click "Run Scraper" to fetch the latest schedule from your email.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Semester Breakdown */}
          {timetableData && timetableData.summary && timetableData.summary.semester_breakdown && Object.keys(timetableData.summary.semester_breakdown).length > 0 && (
            <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-md">
              <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Semester Breakdown
                </h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">
                  Classes grouped by semester
                </p>
              </div>
              <div className="px-4 py-5 sm:p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(timetableData.summary.semester_breakdown).map(([semester, count]) => (
                    <div key={semester} className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-sm font-medium text-gray-900">{semester}</div>
                      <div className="text-2xl font-bold text-blue-600">{count}</div>
                      <div className="text-xs text-gray-500">classes</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <Settings className="h-4 w-4 text-gray-400 mr-2" />
              <span className="text-sm text-gray-500">
                TimeTable Scraper v1.0 - Automated Schedule Management
              </span>
            </div>
            <div className="text-sm text-gray-500">
              Built with React & Flask
            </div>
          </div>
        </div>
      </footer>

      {/* Semester Manager Modal */}
      <SemesterManager
        isOpen={showSemesterManager}
        onClose={() => setShowSemesterManager(false)}
        currentSemesters={config?.semester_filter || []}
        onSave={handleSaveSemesters}
      />
    </div>
  );
}

export default App;