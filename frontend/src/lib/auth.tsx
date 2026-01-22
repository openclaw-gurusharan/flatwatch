'use client';

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

const IDENTITY_URL = process.env.NEXT_PUBLIC_IDENTITY_URL || 'https://aadharcha.in';

export interface User {
  id: string;
  email: string;
  name?: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  validateSession: () => Promise<boolean>;
  login: () => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Validate session with SSO provider
  const validateSession = async (): Promise<boolean> => {
    try {
      const response = await fetch(`${IDENTITY_URL}/api/auth/validate`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          setUser(null);
          return false;
        }
        throw new Error(`Session validation failed: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.valid && data.user) {
        setUser({
          id: data.user.id,
          email: data.user.email,
          name: data.user.name,
          role: data.user.role,
        });
        setError(null);
        return true;
      }

      setUser(null);
      return false;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      setUser(null);
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Redirect to SSO login
  const login = () => {
    const returnUrl = encodeURIComponent(window.location.href);
    window.location.href = `${IDENTITY_URL}/login?return_url=${returnUrl}`;
  };

  // Logout via SSO provider
  const logout = async () => {
    try {
      await fetch(`${IDENTITY_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      setUser(null);
      // Redirect to home after logout
      window.location.href = '/';
    }
  };

  // Validate session on mount
  useEffect(() => {
    validateSession();
  }, []);

  const value: AuthContextType = {
    user,
    loading,
    error,
    validateSession,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
