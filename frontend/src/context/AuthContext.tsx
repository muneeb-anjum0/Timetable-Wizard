import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService } from '../services/api';

interface User {
  id: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string) => Promise<boolean>;
  loginWithGmail: () => Promise<boolean>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored user session
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('user');
      }
    }
    
    // Listen for Gmail OAuth callback
    // Use a ref to store backend origin so handler closure sees latest value
    const backendOriginRef = { current: (window as any).__BACKEND_ORIGIN || null } as { current: string | null };

    const handleGmailAuthMessage = (event: MessageEvent) => {
      // Allow messages from known backend origins (dynamic) or localhost dev origins
      const devPrefixes = [
        'http://localhost:',
        'http://127.0.0.1:',
        'http://192.168.100.250:'
      ];

      const backendOrigin = backendOriginRef.current;

      const allowedFromDev = devPrefixes.some(p => event.origin.startsWith(p));
      const allowedFromBackend = backendOrigin ? event.origin === backendOrigin : false;

      if (!allowedFromDev && !allowedFromBackend) {
        console.log('Ignoring message from unauthorized origin:', event.origin, 'backendOrigin=', backendOrigin);
        return;
      }
      
      console.log('Received OAuth message from:', event.origin, event.data);
      
      console.log('Received message from popup:', event.data);
      
      if (event.data.type === 'GMAIL_AUTH_SUCCESS') {
        const userData = event.data.user;
        console.log('Gmail auth successful, setting user:', userData);
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        setLoading(false);
      } else if (event.data.type === 'GMAIL_AUTH_ERROR') {
        const errorMsg = event.data.error;
        console.error('Gmail auth error:', errorMsg);
        
        // Handle specific scope errors more gracefully
        if (errorMsg && errorMsg.includes('Scope has changed')) {
          console.log('Scope mismatch detected - this is usually harmless, retrying...');
          // Don't show error to user, just set loading to false
          setLoading(false);
        } else {
          console.error('Other Gmail auth error:', errorMsg);
          setLoading(false);
        }
      }
    };
    
    window.addEventListener('message', handleGmailAuthMessage);
    setLoading(false);
    
    return () => {
      window.removeEventListener('message', handleGmailAuthMessage);
    };
  }, []);

  // Keep a ref to backend origin so the message handler can validate dynamically
  const backendOriginRef = React.useRef<string | null>(null);

  const loginWithGmail = async (): Promise<boolean> => {
    try {
      setLoading(true);
      console.log('Starting Gmail OAuth flow...');
      
      const authData = await apiService.getGmailAuthUrl();
      console.log('Got auth URL:', authData.auth_url);
      try {
        const parsed = new URL(authData.auth_url);
        backendOriginRef.current = parsed.origin;
        // also expose globally for older listeners
        (window as any).__BACKEND_ORIGIN = parsed.origin;
        console.log('Set backend origin for postMessage validation:', parsed.origin);
      } catch (err) {
        console.warn('Could not parse auth_url origin', err);
      }
      
      // Open popup window for OAuth
      const popup = window.open(
        authData.auth_url,
        'gmail-auth',
        'width=500,height=600,scrollbars=yes,resizable=yes'
      );
      
      if (!popup) {
        throw new Error('Popup blocked. Please allow popups for this site.');
      }
      
      // The popup will send a message when auth is complete
      return true;
    } catch (error) {
      console.error('Gmail OAuth error:', error);
      setLoading(false);
      return false;
    }
  };

  const login = async (email: string): Promise<boolean> => {
    try {
      setLoading(true);
      console.log('Attempting login with email:', email);
      
      const response = await apiService.login(email);
      console.log('Login response:', response);
      
      if (response.success && response.user) {
        const userData = response.user;
        console.log('Setting user data:', userData);
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        console.log('Login successful');
        return true;
      } else {
        console.error('Login failed - no user data in response:', response);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    login,
    loginWithGmail,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};