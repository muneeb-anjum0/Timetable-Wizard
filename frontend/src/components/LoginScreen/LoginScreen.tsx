import React, { useState } from 'react';
import { Mail, LogIn, AlertCircle, Calendar } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const LoginScreen: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { loginWithGmail } = useAuth();

  const handleGmailLogin = async () => {
    setIsLoading(true);
    setError('');
    try {
      const success = await loginWithGmail();
      if (!success) {
        setError('Gmail authentication failed. Please try again.');
      }
    } catch (error) {
      setError('An error occurred during Gmail authentication. Please try again.');
      console.error('Gmail login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
  <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-3xl shadow-2xl p-10 border border-gray-100">
          {/* Header */}
          <div className="text-center mb-10">
            <div className="w-24 h-24 flex items-center justify-center mx-auto mb-4 rounded-full bg-white shadow-sm">
              <img src="/logoo.svg" alt="Logo" className="w-16 h-16 object-contain p-2" />
            </div>
            <h1 className="text-3xl font-extrabold text-gray-900 mb-2 tracking-tight">
              Timetable Wizard
            </h1>
            <p className="text-base text-gray-600 font-medium">
              Sign in to access your university timetable
            </p>
          </div>

          {/* Gmail OAuth Button */}
          <button
            onClick={handleGmailLogin}
            disabled={isLoading}
            className="w-full bg-white hover:bg-gray-50 disabled:bg-gray-200 disabled:cursor-not-allowed text-gray-900 font-semibold py-3 px-4 rounded-xl transition-colors flex items-center justify-center space-x-2 shadow-lg border border-gray-300"
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
            <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-lg mt-6">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {/* Footer */}
          <div className="mt-10 text-center">
            <p className="text-sm text-gray-500 mb-2">
              Sign in with Gmail to view your timetable.
            </p>
            <a
              href="mailto:muneeb.anjum0@gmail.com"
              className="inline-block text-black hover:text-gray-700 font-semibold text-sm underline transition-colors mt-1"
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