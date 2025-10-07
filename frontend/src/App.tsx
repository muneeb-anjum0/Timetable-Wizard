import React, { useState, useEffect } from 'react';
import './App.css';
import { apiService } from './services/api';
import { TimetableData, ApiResponse, StatusData, ConfigData } from './types/api';
import TimetableTable from './components/TimetableTable/TimetableTable';
import SummaryStats from './components/SummaryStats/SummaryStats';
import StatusIndicator from './components/StatusIndicator/StatusIndicator';
import SemesterManager from './components/SemesterManager/SemesterManager';
import LoginScreen from './components/LoginScreen/LoginScreen';
import { AuthProvider, useAuth } from './context/AuthContext';

function AppContent() {
  const { user, isAuthenticated, logout, loading: authLoading } = useAuth();
  const [timetableData, setTimetableData] = useState<TimetableData | null>(null);
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isScraperRunning, setIsScraperRunning] = useState(false);
  const [isSemesterUpdateRunning, setIsSemesterUpdateRunning] = useState(false);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error' | 'warning'>('idle');
  const [message, setMessage] = useState('');
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);
  const [showSemesterManager, setShowSemesterManager] = useState(false);
  const [operationInProgress, setOperationInProgress] = useState(false);

  // Load initial data on component mount (must be called before early returns)
  useEffect(() => {
    if (isAuthenticated) {
      loadLatestTimetable();
      loadConfig();
      checkStatus();
    }
  }, [isAuthenticated]);

  // Show loading screen while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return <LoginScreen />;
  }

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

  const loadLatestTimetable = async (force = false) => {
    if (operationInProgress && !force) {
      console.log('Operation in progress, skipping timetable load');
      return;
    }
    
    try {
      setIsLoading(true);
      setOperationInProgress(true);
      const response = await apiService.getLatestTimetable();
      if (response.success && response.data) {
        setTimetableData(response.data);
        setStatus('success');
        setMessage(response.cached ? 'Loaded cached data' : 'Data loaded successfully');
      } else {
        setTimetableData(null);
        setStatus('warning');
        setMessage('No timetable data available. Try running a manual scrape.');
      }
    } catch (error) {
      console.error('Error loading timetable:', error);
      setTimetableData(null);
      setStatus('error');
      setMessage('Failed to load timetable data');
    } finally {
      setIsLoading(false);
      setOperationInProgress(false);
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
    if (isScraperRunning || operationInProgress) {
      console.log('Scraper already running or operation in progress');
      return;
    }
    
    try {
      setIsScraperRunning(true);
      setIsLoading(true);
      setOperationInProgress(true);
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
        setTimetableData(null);
      }
    } catch (error) {
      console.error('Error running scraper:', error);
      setStatus('error');
      setMessage('Failed to run scraper');
      setTimetableData(null);
    } finally {
      setIsScraperRunning(false);
      setIsLoading(false);
      setOperationInProgress(false);
    }
  };

  const handleSaveSemesters = async (newSemesters: string[]) => {
    if (isSemesterUpdateRunning || operationInProgress) {
      console.log('Semester update already running or operation in progress');
      return;
    }
    
    try {
      setIsSemesterUpdateRunning(true);
      setIsLoading(true);
      setOperationInProgress(true);
      setStatus('loading');
      setMessage('Updating semester settings...');
      
      const response = await apiService.updateSemesters(newSemesters);
      if (response.success) {
        // Reload config to get updated data
        await loadConfig();
        
        // Clear old timetable data since filters changed
        setTimetableData(null);
        
        setStatus('success');
        setMessage(`Successfully updated ${newSemesters.length} allowed semesters. Run scraper to apply new filters.`);
        
        // Automatically run scraper if there are allowed semesters
        if (newSemesters.length > 0) {
          setMessage(`Successfully updated ${newSemesters.length} allowed semesters. Running scraper...`);
          // Small delay to let user see the update message
          setTimeout(() => {
            runScraper();
          }, 1000);
        }
      } else {
        setStatus('error');
        setMessage(response.error || 'Failed to update semesters');
      }
    } catch (error) {
      console.error('Error updating semesters:', error);
      setStatus('error');
      setMessage('Failed to update semesters');
    } finally {
      setIsSemesterUpdateRunning(false);
      setIsLoading(false);
      setOperationInProgress(false);
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
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between py-4 sm:py-6">
            <div className="flex items-center mb-3 sm:mb-0">
              <img src="/logoo.svg" alt="Logo" className="h-7 w-7 sm:h-9 sm:w-9 mr-2 sm:mr-3" />
              <div className="flex flex-col">
                <div className="flex items-center">
                  <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">TimeTable Scraper</h1>
                </div>
                <p className="text-xs sm:text-sm text-gray-500">Welcome, {user?.email}</p>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
              <div className="text-xs sm:text-sm text-gray-500">
                Last updated: {formatLastUpdate(lastUpdate)}
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={logout}
                  className="flex items-center space-x-1 text-gray-600 hover:text-gray-900 px-2 py-1 rounded-lg hover:bg-gray-100 transition-colors text-xs sm:text-sm"
                >
                  <img src="/logout.svg" alt="Logout" className="h-3 w-3 sm:h-4 sm:w-4" />
                  <span>Sign Out</span>
                </button>
                <button
                  onClick={() => setShowSemesterManager(true)}
                  className="inline-flex items-center px-2 sm:px-3 py-2 border border-gray-300 text-xs sm:text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <img src="/setting.svg" alt="Settings" className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                  <span className="hidden sm:inline">Semesters </span>({config?.semester_filter?.length || 0})
                </button>
                <button
                  onClick={runScraper}
                  disabled={isScraperRunning || operationInProgress}
                  className="inline-flex items-center px-3 sm:px-4 py-2 border-2 border-gray-400 text-xs sm:text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <img src="/refresh.svg" alt="Refresh" className={`h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2 ${isScraperRunning ? 'animate-spin' : ''}`} />
                  <span className="hidden sm:inline">
                    {isScraperRunning ? 'Scraping...' : isSemesterUpdateRunning ? 'Updating...' : 'Run Scraper'}
                  </span>
                  <span className="sm:hidden">
                    {isScraperRunning ? '⏳' : isSemesterUpdateRunning ? '🔄' : '▶️'}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-4 sm:py-6 px-4 sm:px-6 lg:px-8">
        <div className="space-y-4 sm:space-y-6">
          
          {/* Status Indicator */}
          {message && (
            <div>
              <StatusIndicator 
                status={status === 'loading' ? 'loading' : status === 'success' ? 'success' : status === 'warning' ? 'warning' : 'error'} 
                message={message} 
              />
            </div>
          )}

          {/* Summary Stats */}
          {timetableData && (
            <div>
              <SummaryStats data={timetableData} />
            </div>
          )}

          {/* Timetable */}
          <div className="bg-white shadow overflow-hidden rounded-md sm:rounded-lg">
            <div className="px-3 sm:px-4 py-4 sm:py-5 lg:px-6 border-b border-gray-200">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div className="mb-2 sm:mb-0">
                  <h3 className="text-base sm:text-lg leading-6 font-medium text-gray-900">
                    Class Schedule
                  </h3>
                  <p className="mt-1 max-w-2xl text-xs sm:text-sm text-gray-500">
                    {timetableData 
                      ? `${timetableData.for_day} - ${new Date(timetableData.for_date).toLocaleDateString()}`
                      : 'No data available'
                    }
                  </p>
                </div>
                <div className="flex items-center">
                  <img src="/pulse.svg" alt="Pulse" className="h-4 w-4 sm:h-5 sm:w-5 text-gray-400 mr-2" />
                  <span className="text-xs sm:text-sm text-gray-500">
                    {timetableData?.items?.length || 0} classes
                  </span>
                </div>
              </div>
            </div>
            
            <div className="p-0">
              {timetableData ? (
                <TimetableTable items={timetableData.items} />
              ) : (
                <div className="text-center py-8 sm:py-12 px-4">
                  <img src="/day.svg" alt="Calendar" className="mx-auto h-8 w-8 sm:h-12 sm:w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No schedule data</h3>
                  <p className="mt-1 text-xs sm:text-sm text-gray-500">
                    Click "Run Scraper" to fetch the latest schedule from your email.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Semester Breakdown */}
          {timetableData && timetableData.summary && timetableData.summary.semester_breakdown && Object.keys(timetableData.summary.semester_breakdown).length > 0 && (
            <div className="bg-white shadow overflow-hidden rounded-md sm:rounded-lg">
              <div className="px-3 sm:px-4 py-4 sm:py-5 lg:px-6 border-b border-gray-200">
                <h3 className="text-base sm:text-lg leading-6 font-medium text-gray-900">
                  Semester Breakdown
                </h3>
                <p className="mt-1 max-w-2xl text-xs sm:text-sm text-gray-500">
                  Classes grouped by semester
                </p>
              </div>
              <div className="px-3 sm:px-4 py-4 sm:py-5 lg:px-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  {Object.entries(timetableData.summary.semester_breakdown).map(([semester, count]) => (
                    <div key={semester} className="bg-gray-50 p-3 sm:p-4 rounded-lg">
                      <div className="text-xs sm:text-sm font-medium text-gray-900">{semester}</div>
                      <div className="text-xl sm:text-2xl font-bold text-blue-600">{count}</div>
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
              <img src="/setting.svg" alt="Settings" className="h-4 w-4 text-gray-400 mr-2" />
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

// Main App component with AuthProvider
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;