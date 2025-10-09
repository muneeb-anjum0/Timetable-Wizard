import React, { useState } from 'react';
import { Mail, LogIn, AlertCircle, Calendar } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const LoginScreen: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isExiting, setIsExiting] = useState(false);
  const { loginWithGmail } = useAuth();

  const handleGmailLogin = async () => {
    setIsLoading(true);
    setError('');
    try {
      const success = await loginWithGmail();
      if (success) {
        // Start exit animation before actual redirect
        setIsExiting(true);
        // Let animation play for a bit before auth context handles the redirect
        setTimeout(() => {
          // The auth context will handle the redirect
        }, 300);
      } else {
        setError('Gmail authentication failed. Please try again.');
      }
    } catch (error) {
      setError('An error occurred during Gmail authentication. Please try again.');
      console.error('Gmail login error:', error);
    } finally {
      if (!isExiting) {
        setIsLoading(false);
      }
    }
  };

  return (
  <div className={`min-h-screen bg-white flex items-center justify-center p-4 ${isExiting ? 'animate-login-exit' : 'animate-fade-in'}`}>
      <div className="max-w-md w-full">
        <div className={`bg-white rounded-3xl shadow-2xl p-10 border border-gray-100 ${isExiting ? '' : 'animate-fade-in-up'}`}>
          {/* Header */}
          <div className="text-center mb-10">
            <div className="w-24 h-24 flex items-center justify-center mx-auto mb-4 rounded-full bg-white shadow-sm animate-gentle-scale">
              <img src="/logoo.svg" alt="Logo" className="w-16 h-16 object-contain p-2" />
            </div>
            <h1 className="text-3xl font-extrabold text-gray-900 mb-2 tracking-tight animate-fade-in animation-delay-200">
              Timetable Wizard
            </h1>
            <p className="text-base text-gray-600 font-medium animate-fade-in animation-delay-300">
              Sign in to access your university timetable
            </p>
          </div>

          {/* Gmail OAuth Button */}
          <button
            onClick={handleGmailLogin}
            disabled={isLoading}
            className="w-full bg-white hover:bg-gray-50 disabled:bg-gray-200 disabled:cursor-not-allowed text-gray-900 font-semibold py-3 px-4 rounded-xl transition-all duration-300 flex items-center justify-center space-x-2 shadow-lg border border-gray-300 hover:scale-105 hover:shadow-xl animate-fade-in animation-delay-400"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-400"></div>
                <span className="text-gray-700">Connecting to Gmail...</span>
              </>
            ) : (
              <>
                <img src="/gmail.svg" alt="Gmail" className="w-7 h-7 mr-2" />
                <span className="text-gray-900">Sign in with Gmail</span>
              </>
            )}
          </button>

          {error && (
            <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-lg mt-6 border border-red-200 animate-fade-in">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {/* Footer */}
          <div className="mt-10 text-center animate-fade-in animation-delay-500">
            <p className="text-sm text-gray-500 mb-2">
              Sign in with Gmail to view your timetable.
            </p>
            <a
              href="mailto:muneeb.anjum0@gmail.com"
              className="inline-block text-black hover:text-gray-700 font-semibold text-sm underline transition-all duration-300 mt-1 hover:scale-105"
              target="_blank"
              rel="noopener noreferrer"
            >
              Need help? Contact Support
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;