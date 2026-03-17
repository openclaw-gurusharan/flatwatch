'use client';

import { ReactNode } from 'react';
import { useAuth } from './auth';

interface ProtectedRouteProps {
  children: ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading, login, error } = useAuth();

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
        <div className="text-center space-y-4">
          <div className="space-y-2">
            <p className="text-[#333]">Sign in required</p>
            <p className="text-[#999]">Use the local development account to access FlatWatch.</p>
            {error ? <p className="text-sm text-[rgb(255,97,26)]">{error}</p> : null}
          </div>
          <button
            type="button"
            onClick={() => void login()}
            className="inline-flex h-12 items-center justify-center rounded-full bg-[rgb(255,97,26)] px-6 font-medium text-white shadow-[0_2px_8px_rgba(255,97,26,0.3)] transition-all hover:shadow-[0_4px_12px_rgba(255,97,26,0.4)] active:scale-95"
          >
            Sign in
          </button>
        </div>
      </div>
    );
  }

  // User is authenticated, render children
  return <>{children}</>;
}
