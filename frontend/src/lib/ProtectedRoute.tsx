'use client';

import { useEffect, ReactNode, useRef } from 'react';
import { useAuth } from './auth';

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading, login } = useAuth();
  const hasAttemptedLogin = useRef(false);

  useEffect(() => {
    if (!loading && !user && !hasAttemptedLogin.current) {
      hasAttemptedLogin.current = true;
      void login();
    }
  }, [loading, user, login]);

  // Show loading while validating session
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 animate-pulse rounded-full bg-[rgb(255,97,26)]" />
          <span className="text-[#999]">Verifying session...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="text-center">
          <p className="text-[#999]">Signing in...</p>
        </div>
      </div>
    );
  }

  // User is authenticated, render children
  return <>{children}</>;
}
