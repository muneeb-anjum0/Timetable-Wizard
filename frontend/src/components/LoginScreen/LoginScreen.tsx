import React, { useState } from 'react';
import { motion } from 'framer-motion';
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
    <motion.div
      initial={{ opacity: 0, y: -40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3 }}
      className={`min-h-screen bg-white flex items-center justify-center p-4`}
    >
      <motion.div
        initial={{ opacity: 0, y: -40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.05 }}
        className="max-w-md w-full"
      >
        <motion.div
          initial={{ opacity: 0, y: -40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.1 }}
          className="bg-white rounded-3xl shadow-2xl p-10 border border-gray-100"
        >
          {/* Header */}
          <div className="text-center mb-10">
            <motion.div
              initial={{ opacity: 0, y: -40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.15 }}
              className="w-24 h-24 flex items-center justify-center mx-auto mb-4 rounded-full bg-white shadow-sm"
            >
              <img src="/logoo.svg" alt="Logo" className="w-16 h-16 object-contain p-2" />
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: -40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.2 }}
              className="text-3xl font-extrabold text-gray-900 mb-2 tracking-tight"
            >
              Timetable Wizard
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: -40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.25 }}
              className="text-base text-gray-600 font-medium"
            >
              Sign in to access your university timetable
            </motion.p>
          </div>
          {/* Gmail OAuth Button */}
          <motion.button
            initial={{ opacity: 0, y: -40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.3 }}
            onClick={handleGmailLogin}
            disabled={isLoading}
            className="w-full bg-white hover:bg-gray-50 disabled:bg-gray-200 disabled:cursor-not-allowed text-gray-900 font-semibold py-3 px-4 rounded-xl transition-all duration-300 flex items-center justify-center space-x-2 shadow-lg border border-gray-300 hover:scale-105 hover:shadow-xl"
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
          </motion.button>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.35 }}
              className="flex items-center space-x-2 text-red-600 bg-red-50 p-3 rounded-lg mt-6 border border-red-200"
            >
              <AlertCircle className="w-5 h-5" />
              <span className="text-sm">{error}</span>
            </motion.div>
          )}
          {/* Footer */}
          <motion.div
            initial={{ opacity: 0, y: -40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: 'spring', stiffness: 600, damping: 18, duration: 0.3, delay: 0.4 }}
            className="mt-10 text-center"
          >
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
          </motion.div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}

export default LoginScreen;