// AuthContext.tsx
import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { auth } from '../services/authService.tsx';

interface User {
  sub: string;
  email: string;
  name?: string;
  picture?: string;
  email_verified: boolean;
  roles: string[];
  [key: string]: unknown;
}

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  login: () => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    let mounted = true;

    const checkAuth = async () => {
      // Skip auth check if we're on home page or logging out
      if (window.location.pathname === '/' || sessionStorage.getItem('isLoggingOut')) {
        setIsAuthenticated(false);
        setUser(null);
        setIsLoading(false);
        return;
      }

      // Skip if we're in the callback process
      if (window.location.pathname.includes('/callback')) {
        setIsLoading(false);
        return;
      }

      // Use AbortController for cleanup
      const controller = new AbortController();

      try {
        const userData = await auth.getUser();

        // Check if component is still mounted and request wasn't aborted
        if (!mounted || controller.signal.aborted) return;

        if (userData) {
          setUser(userData);
          setIsAuthenticated(true);
        } else {
          setUser(null);
          setIsAuthenticated(false);
        }
      } catch (error) {
        if (!mounted || controller.signal.aborted) return;
        setUser(null);
        setIsAuthenticated(false);
      } finally {
        if (mounted && !controller.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    void checkAuth();

    return () => {
      mounted = false;
    };
  }, []); // Keep empty dependency array

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      sessionStorage.setItem('isLoggingOut', 'true');
      setIsAuthenticated(false);
      setUser(null);
      await auth.logout();
    } catch (error) {
      console.error('Logout failed:', error);
      window.location.href = '/';
    }
  };

  // Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo(() => ({
    isAuthenticated,
    isLoading,
    user,
    login: auth.login,
    logout: handleLogout
  }), [isAuthenticated, isLoading, user, handleLogout]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export type { AuthContextType, User };