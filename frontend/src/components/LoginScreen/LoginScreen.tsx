import React, { useState } from 'react';
import { Mail, LogIn, AlertCircle, Calendar } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const LoginScreen: React.FC = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showManualLogin, setShowManualLogin] = useState(false);
  const { login, loginWithGmail } = useAuth();

  const handleGmailLogin = async () => {
    setIsLoading(true);
    setError('');

    try {
      console.log('Starting Gmail OAuth login...');
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email.trim()) {
      setError('Please enter your email address');
      return;
    }

    if (!email.includes('@')) {
      setError('Please enter a valid email address');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      console.log('Submitting login for:', email.trim().toLowerCase());
      const success = await login(email.trim().toLowerCase());
      console.log('Login result:', success);
      
      if (!success) {
        setError('Login failed. Please try again.');
      }
    } catch (error) {
      setError('An error occurred during login. Please try again.');
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <Calendar className="w-8 h-8 text-blue-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Timetable Wizard
            </h1>
            <p className="text-gray-600">
              Enter your email to access your personal timetable
            </p>
          </div>

          {/* Login Options */}
          <div className="space-y-4">
            {/* Gmail OAuth Button */}
            <button
              onClick={handleGmailLogin}
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Connecting to Gmail...</span>
                </>
              ) : (
                <>
                  <Mail className="w-5 h-5" />
                  <span>Sign in with Gmail</span>
                </>
              )}
            </button>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">or</span>
              </div>
            </div>

            {/* Manual Email Entry (for testing) */}
            <button
              onClick={() => setShowManualLogin(!showManualLogin)}
              className="w-full text-sm text-gray-600 hover:text-gray-900 py-2"
            >
              {showManualLogin ? 'Hide manual login' : 'Use manual email login (for testing)'}
            </button>
          </div>

          {error && (
            <div className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-lg">
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm">{error}</span>
            </div>
          )}

          {/* Manual Login Form (hidden by default) */}
          {showManualLogin && (
            <form onSubmit={handleSubmit} className="space-y-4 mt-4 pt-4 border-t border-gray-200">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address (Testing Only)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors"
                    placeholder="your.email@example.com"
                    disabled={isLoading}
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Creating Account...</span>
                  </>
                ) : (
                  <>
                    <LogIn className="w-5 h-5" />
                    <span>Create Test Account</span>
                  </>
                )}
              </button>
            </form>
          )}

          {/* Footer */}
          <div className="mt-8 text-center">
            <p className="text-xs text-gray-500">
              Sign in with your Gmail account to access your university timetable data.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;