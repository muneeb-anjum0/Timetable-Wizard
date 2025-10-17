import React, { useState } from 'react';
import { Mail, LogIn, AlertCircle, Calendar } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const LoginScreen: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isExiting, setIsExiting] = useState(false);
  const { loginWithGmail } = useAuth();

  const handleGmailLogin = async () => {
    console.log('[Mobile Debug] Login button clicked');
    console.log('[Mobile Debug] User agent:', navigator.userAgent);
    console.log('[Mobile Debug] Current URL:', window.location.href);
    console.log('[Mobile Debug] Screen dimensions:', {
      width: window.screen.width,
      height: window.screen.height,
      availWidth: window.screen.availWidth,
      availHeight: window.screen.availHeight
    });
    
    setIsLoading(true);
    setError('');
    try {
      console.log('[Mobile Debug] Starting Gmail login flow...');
      const success = await loginWithGmail();
      console.log('[Mobile Debug] Login flow result:', success);
      
      if (success) {
        console.log('[Mobile Debug] Login successful, starting exit animation');
        // Start exit animation before actual redirect
        setIsExiting(true);
        // Let animation play for a bit before auth context handles the redirect
        setTimeout(() => {
          // The auth context will handle the redirect
          console.log('[Mobile Debug] Exit animation complete');
        }, 300);
      } else {
        console.error('[Mobile Debug] Login failed');
        setError('Gmail authentication failed. Please try again.');
      }
    } catch (error) {
      console.error('[Mobile Debug] Login error caught:', error);
      setError('An error occurred during Gmail authentication. Please try again.');
    } finally {
      if (!isExiting) {
        console.log('[Mobile Debug] Setting loading to false');
        setIsLoading(false);
      }
    }
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4 ${isExiting ? 'animate-login-exit-smooth' : 'animate-drop-bounce'}`}>
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-10 left-10 w-20 h-20 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
        <div className="absolute top-32 right-20 w-32 h-32 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-20 w-24 h-24 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-2000"></div>
        <div className="absolute bottom-32 right-10 w-28 h-28 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-500"></div>
      </div>
      
      <div className="max-w-md w-full relative z-10">
        <div className={`bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-10 border border-white/50 ${isExiting ? '' : 'animate-drop-bounce delay-100'}`}>
          {/* Header */}
          <div className="text-center mb-10">
            
            <h1 className="text-4xl font-extrabold text-gray-900 mb-3 tracking-tight animate-drop-bounce delay-200" style={{color: '#1a1a1a', textShadow: '0 0 20px rgba(59, 130, 246, 0.15)'}}>
              Timetable Wizard
            </h1>
            <p className="text-base text-gray-700 font-medium animate-drop-bounce delay-250">
              Sign in with your SZABIST account to continue
            </p>
          </div>

          {/* Gmail OAuth Button */}
          <button
            onClick={handleGmailLogin}
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-white to-gray-50 hover:from-blue-50 hover:to-indigo-50 active:from-blue-100 active:to-indigo-100 disabled:from-gray-100 disabled:to-gray-200 disabled:cursor-not-allowed text-gray-900 font-semibold py-4 px-6 rounded-2xl transition-all duration-300 flex items-center justify-center space-x-3 shadow-xl border-2 border-blue-200/50 hover:border-blue-300 active:border-blue-400 hover:scale-105 active:scale-95 hover:shadow-2xl animate-drop-bounce delay-300 group touch-manipulation"
            style={{ WebkitTapHighlightColor: 'transparent' }}
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-2 border-blue-500 border-t-transparent"></div>
                <span className="text-gray-700 text-lg">Connecting to Gmail...</span>
              </>
            ) : (
              <>
                <img src="/gmail.svg" alt="Gmail" className="w-8 h-8 transition-transform duration-300 group-hover:scale-110" />
                <span className="text-gray-900 text-lg font-semibold">Sign in with Gmail</span>
              </>
            )}
          </button>

          {error && (
            <div className="flex items-center space-x-2 text-red-700 bg-gradient-to-r from-red-50 to-pink-50 p-4 rounded-2xl mt-6 border-2 border-red-200/50 backdrop-blur-sm animate-fade-in shadow-lg">
              <AlertCircle className="w-5 h-5 animate-pulse" />
              <div className="flex-1">
                <span className="text-sm font-medium">{error}</span>
                {error.includes('Popup blocked') && (
                  <div className="mt-2 text-xs text-red-600">
                    On mobile? Try refreshing and tapping the login button again. The page will redirect to complete authentication.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Feature highlights */}
          <div className="mt-8 space-y-3 animate-drop-bounce delay-400">
            <div className="flex items-center space-x-3 text-sm text-gray-600 bg-blue-50/50 p-3 rounded-xl border border-blue-100">
              <Calendar className="w-4 h-4 text-blue-500" />
              <span>Smart timetable parsing</span>
            </div>
            <div className="flex items-center space-x-3 text-sm text-gray-600 bg-indigo-50/50 p-3 rounded-xl border border-indigo-100">
              <Mail className="w-4 h-4 text-indigo-500" />
              <span>Email integration</span>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 text-center">
            
            <a
              href="mailto:muneeb.anjum0@gmail.com"
              className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-semibold text-sm transition-all duration-300 hover:scale-105 bg-blue-50/50 px-4 py-2 rounded-xl border border-blue-100"
              target="_blank"
              rel="noopener noreferrer"
            >
              <span>Need help? Contact Support</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;