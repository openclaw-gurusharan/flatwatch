import { ReactNode } from "react";

interface ResponsiveGridProps {
  children: ReactNode;
  className?: string;
}

/**
 * Mobile-first responsive grid component.
 * - Mobile: 1 column (stacked)
 * - Tablet (768px+): 2 columns
 * - Desktop (1024px+): 3 columns
 */
export function ResponsiveGrid({ children, className = "" }: ResponsiveGridProps) {
  return (
    <div className={`mobile-card-stack ${className}`}>
      {children}
    </div>
  );
}

interface ResponsiveCardProps {
  children: ReactNode;
  className?: string;
}

/**
 * Mobile-safe card component with proper touch targets.
 */
export function ResponsiveCard({ children, className = "" }: ResponsiveCardProps) {
  return (
    <div
      className={`bg-white rounded-2xl shadow-sm p-4 md:p-6 ${className}`}
    >
      {children}
    </div>
  );
}
