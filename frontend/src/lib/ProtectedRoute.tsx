'use client';

import { useEffect, ReactNode } from 'react';
import { useAuth } from './auth';

const IDENTITY_URL = process.env.NEXT_PUBLIC_IDENTITY_URL || 'https://aadharcha.in';

interface ProtectedRouteProps {
  children: ReactNode;
}

/**
 * ProtectedRoute component that validates SSO session before rendering children.
 * Redirects to SSO login page if session is invalid.
 */
export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading, error, validateSession } = useAuth();

  useEffect(() => {
    // Re-validate session when component mounts
    validateSession();
  }, [validateSession]);

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

  // If not authenticated, redirect will be handled by useAuth hook
  // Show a brief message before redirect happens
  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="text-center">
          <p className="text-[#999]">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  // User is authenticated, render children
  return <>{children}</>;
}
