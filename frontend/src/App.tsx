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
  // Custom sign out confirmation dialog
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const handleLogoutClick = () => setShowLogoutConfirm(true);
  const handleLogoutConfirm = () => {
    setShowLogoutConfirm(false);
    logout();
  };
  const handleLogoutCancel = () => setShowLogoutConfirm(false);
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

  // Computed state
  const noSemestersConfigured = config && (!config.semester_filter || config.semester_filter.length === 0);

  // Load initial data on component mount (must be called before early returns)
  useEffect(() => {
    if (isAuthenticated) {
      loadLatestTimetable();
      loadConfig();
      checkStatus();
    }
  }, [isAuthenticated]);

  // Check for no semesters configured and set warning message
  useEffect(() => {
    if (config && timetableData && noSemestersConfigured && !isScraperRunning && !operationInProgress) {
      setStatus('warning');
      setMessage('No semesters configured. Please add semesters to filter and organize your schedule.');
    }
  }, [config, timetableData, noSemestersConfigured, isScraperRunning, operationInProgress]);

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

    // Check if semesters are configured before running scraper
    if (!config?.semester_filter || config.semester_filter.length === 0) {
      setStatus('error');
      setMessage('No semesters configured. Please add semesters before running the scraper.');
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

  // Special version of runScraper that bypasses semester validation (used for auto-run after updating semesters)
  const runScraperWithSemesters = async (semestersList: string[]) => {
    if (isScraperRunning || operationInProgress) {
      console.log('Scraper already running or operation in progress');
      return;
    }

    // This version skips the semester validation since we know semesters are configured
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
          // Small delay to let config state update, then run scraper
          setTimeout(() => {
            runScraperWithSemesters(newSemesters);
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
    <div className="min-h-screen bg-gray-50 animate-dashboard-enter">
      {/* Header */}
      <header className="bg-white shadow sticky top-0 z-30 animate-fall-down">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between py-3 sm:py-4">
            <div className="flex items-center gap-4 mb-2 sm:mb-0 animate-fall-down animation-delay-50">
              <img src="/logoo.svg" alt="Logo" className="h-9 w-9 sm:h-11 sm:w-11 p-1 bg-white transition-transform duration-300 hover:scale-110 animate-fall-down animation-delay-100" style={{overflow: 'visible'}} />
              <div className="flex items-center bg-blue-50 rounded-full px-3 py-1 shadow transition-all duration-200 hover:shadow-md animate-fall-down animation-delay-150">
                <span className="text-xs sm:text-sm text-blue-700 font-semibold">Welcome</span>
                <span className="mx-2 text-xs sm:text-sm font-mono text-blue-900">{user?.email}</span>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
              <div className="flex items-center gap-2 text-xs sm:text-sm text-gray-500 bg-gray-100 rounded-full px-3 py-1 shadow transition-all duration-200 hover:shadow-md animate-fall-down animation-delay-200">
                <img src="/refresh.svg" alt="Last Updated" className="h-4 w-4 mr-1" />
                <span>Last updated:</span>
                <span className="font-mono text-blue-700">{formatLastUpdate(lastUpdate)}</span>
              </div>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={runScraper}
                  disabled={isScraperRunning || operationInProgress}
                  className="inline-flex items-center px-3 sm:px-4 py-2 border-2 border-gray-400 text-xs sm:text-sm font-medium rounded-full shadow text-gray-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-md animate-fall-down animation-delay-250"
                >
                  <img src="/refresh.svg" alt="Refresh" className={`h-4 w-4 mr-2 transition-transform duration-300 ${isScraperRunning ? 'animate-spin' : ''}`} />
                  <span className="hidden sm:inline">
                    {isScraperRunning ? 'Scraping...' : isSemesterUpdateRunning ? 'Updating...' : 'Run Scraper'}
                  </span>
                  <span className="sm:hidden">
                    {isScraperRunning ? '⏳' : isSemesterUpdateRunning ? '🔄' : '▶️'}
                  </span>
                </button>
                <button
                  onClick={() => setShowSemesterManager(true)}
                  className={`inline-flex items-center px-3 py-2 border text-xs sm:text-sm font-medium rounded-full text-gray-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-400 transition-all duration-200 hover:shadow-md animate-fall-down animation-delay-300 ${
                    timetableData && config && (!config.semester_filter || config.semester_filter.length === 0) 
                      ? 'animate-pulse-glow-blue border-blue-400' 
                      : 'border-gray-300'
                  }`}
                >
                  <img src="/setting.svg" alt="Settings" className="h-4 w-4 mr-2" />
                  <span className="hidden sm:inline">Semesters </span>({config?.semester_filter?.length || 0})
                </button>
                <div className="relative inline-block animate-fall-down animation-delay-350">
                  <button
                    onClick={handleLogoutClick}
                    className="flex items-center space-x-1 text-gray-600 hover:text-red-600 px-3 py-2 rounded-full hover:bg-red-50 transition-all duration-200 text-xs sm:text-sm border border-gray-200 hover:shadow-md"
                  >
                    <img src="/logout.svg" alt="Logout" className="h-4 w-4" />
                    <span>Sign Out</span>
                  </button>
                  {showLogoutConfirm && (
                    <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-50 p-4 text-center animate-modal-enter">
                      <div className="text-gray-700 mb-3 text-sm">Are you sure you want to sign out?</div>
                      <div className="flex justify-center gap-2">
                        <button
                          onClick={handleLogoutCancel}
                          className="inline-flex items-center px-3 py-2 border-2 border-gray-400 text-xs sm:text-sm font-medium rounded-full shadow text-gray-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-400 transition-colors duration-200"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={handleLogoutConfirm}
                          className="inline-flex items-center px-3 py-2 border-2 border-red-400 text-xs sm:text-sm font-medium rounded-full shadow text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-400 transition-colors duration-200"
                        >
                          Sign Out
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-4 sm:py-6 px-4 sm:px-6 lg:px-8">
        <div className="space-y-4 sm:space-y-6">
          
          {/* Status Indicator - Always show when config is available */}
          {config && (
            <div>
              <StatusIndicator 
                status={status === 'loading' ? 'loading' : status === 'success' ? 'success' : status === 'warning' ? 'warning' : status === 'error' ? 'error' : 'success'} 
                message={message || (config.semester_filter && config.semester_filter.length > 0 ? `${config.semester_filter.length} semester(s) configured` : 'Ready to configure semesters')} 
              />
            </div>
          )}

          {/* Summary Stats - Always show when config is available */}
          {config && (
            <div>
              {timetableData && !isScraperRunning ? (
                <SummaryStats data={timetableData} config={config || undefined} />
              ) : (
                // Show placeholder stats when no semesters configured
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <div className="bg-white overflow-hidden shadow rounded-lg transition-all duration-300 hover:shadow-md">
                    <div className="p-5">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <img src="/courses.svg" alt="Total Classes" className="w-8 h-8 opacity-50" />
                        </div>
                        <div className="ml-5 w-0 flex-1">
                          <dl>
                            <dt className="text-sm font-medium text-gray-500 truncate">
                              Total Classes
                            </dt>
                            <dd className="text-lg font-medium text-gray-400">
                              0
                            </dd>
                          </dl>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white overflow-hidden shadow rounded-lg transition-all duration-300 hover:shadow-md">
                    <div className="p-5">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <img src="/uniqueCourses.svg" alt="Unique Courses" className="w-8 h-8 opacity-50" />
                        </div>
                        <div className="ml-5 w-0 flex-1">
                          <dl>
                            <dt className="text-sm font-medium text-gray-500 truncate">
                              Unique Courses
                            </dt>
                            <dd className="text-lg font-medium text-gray-400">
                              0
                            </dd>
                          </dl>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white overflow-hidden shadow rounded-lg transition-all duration-300 hover:shadow-md">
                    <div className="p-5">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <img src="/faculty.svg" alt="Faculty Members" className="w-8 h-8 opacity-50" />
                        </div>
                        <div className="ml-5 w-0 flex-1">
                          <dl>
                            <dt className="text-sm font-medium text-gray-500 truncate">
                              Faculty Members
                            </dt>
                            <dd className="text-lg font-medium text-gray-400">
                              0
                            </dd>
                          </dl>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white overflow-hidden shadow rounded-lg transition-all duration-300 hover:shadow-md">
                    <div className="p-5">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <img src="/day.svg" alt="Day" className="w-8 h-8 opacity-50" />
                        </div>
                        <div className="ml-5 w-0 flex-1">
                          <dl>
                            <dt className="text-sm font-medium text-gray-500 truncate">
                              Day
                            </dt>
                            <dd className="text-lg font-medium text-gray-400">
                              Wednesday
                            </dd>
                          </dl>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white overflow-hidden shadow rounded-lg col-span-1 md:col-span-2 lg:col-span-4 transition-all duration-300 hover:shadow-md">
                    <div className="p-5">
                      <div className="flex items-center mb-2">
                        <span className="font-semibold text-gray-500 text-base">Semester Breakdown</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <span className="text-gray-400 text-xs">No semester data available</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Timetable - Only show if config is loaded, semesters are configured, scraper is NOT running, and timetable data is present */}
          {config && !noSemestersConfigured && !isScraperRunning && timetableData && timetableData.items && timetableData.items.length > 0 && (
            <div className="bg-white shadow overflow-hidden rounded-md sm:rounded-lg">
              <div className="px-4 py-4 lg:px-6 border-b border-gray-100 bg-blue-50 rounded-t-lg">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                  <div className="mb-2 sm:mb-0">
                    <h3 className="text-lg font-semibold text-gray-900 tracking-tight">Class Schedule</h3>
                  </div>
                  <div className="flex items-center gap-2">
                    <img src="/pulse.svg" alt="Pulse" className="h-5 w-5 text-blue-400" />
                    <span className="text-sm text-blue-700 font-medium">
                      {timetableData?.items?.length || 0} classes
                    </span>
                  </div>
                </div>
              </div>
              <div className="p-0">
                <TimetableTable items={timetableData.items} />
              </div>
            </div>
          )}

          {/* Show Configure Semesters card when: no semesters configured, scraper running, semester update running, or no timetable data */}
          {(noSemestersConfigured || isScraperRunning || isSemesterUpdateRunning || !timetableData || !timetableData.items || timetableData.items.length === 0) && (
            <div className="bg-white rounded-lg shadow p-8 text-center animate-fall-down animation-delay-500">
              <div className="text-gray-500 mb-4 animate-fall-down animation-delay-550">
                <img src="/setting.svg" alt="Setting" className="mx-auto mb-4 h-16 w-16 text-blue-400 animate-fall-down animation-delay-600" />
                <h3 className="text-lg font-medium text-gray-900 mb-2 animate-fall-down animation-delay-650">Configure Semesters to View Schedule</h3>
                <p className="text-gray-500 mb-6 animate-fall-down animation-delay-700">You have schedule data available, but you need to add semesters to organize and filter your classes properly.</p>
                <button
                  onClick={() => setShowSemesterManager(true)}
                  className="inline-flex items-center px-3 sm:px-4 py-2 border-2 border-gray-400 text-xs sm:text-sm font-medium rounded-full shadow text-gray-700 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-400 transition-all duration-200 hover:shadow-md hover:scale-105 animate-fall-down animation-delay-750"
                >
                  <img src="/add.svg" alt="Add" className="h-4 w-4 mr-2" />
                  <span className="hidden sm:inline">Add Semesters</span>
                  <span className="sm:hidden">Add</span>
                </button>
              </div>
            </div>
          )}

          {/* Semester Breakdown removed to avoid duplication */}
        </div>
      </main>

      {/* Minimal Footer */}
      <footer className="bg-transparent border-0">
        <div className="w-full py-1 text-center text-xs text-gray-300">
          &copy; {new Date().getFullYear()} Timetable Wizard
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