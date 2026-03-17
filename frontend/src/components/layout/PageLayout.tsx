'use client';

import type { ReactNode } from 'react';
import Link from 'next/link';
import { MobileNav } from '@/components/mobile/MobileNav';
import { WalletMultiButton } from '@solana/wallet-adapter-react-ui';

export function PageLayout({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-white text-[#333]">
      <header className="sticky top-0 z-30 border-b border-[rgb(238,238,238)] bg-white/95 backdrop-blur">
        <div className="container-responsive flex items-center justify-between gap-6 py-5">
          <div className="min-w-0">
            <Link
              href="/dashboard"
              className="text-[2rem] leading-none text-[#333]"
              style={{ fontFamily: 'var(--font-sacramento)' }}
            >
              FlatWatch
            </Link>
            <p className="mt-1 text-sm text-[#999]">Transparency, evidence, and challenge workflows</p>
          </div>
          <div className="flex items-center gap-3">
            <WalletMultiButton className="!h-10 !rounded-full !bg-[rgb(255,97,26)] !px-4 !text-sm !font-medium !text-white !shadow-[0_2px_8px_rgba(255,97,26,0.3)]" />
            <MobileNav />
          </div>
        </div>
      </header>

      <div className="container-responsive py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold tracking-tight text-[#333]">{title}</h1>
          {description ? <p className="mt-2 max-w-2xl text-sm text-[#666]">{description}</p> : null}
        </div>

        <div className="space-y-6">{children}</div>
      </div>
    </div>
  );
}
