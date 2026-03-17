'use client';

import type { PortfolioTrustState } from '@/lib/trust';

const IDENTITY_URL = process.env.NEXT_PUBLIC_IDENTITY_WEB_URL || 'http://localhost:3000';

const STATE_META: Record<PortfolioTrustState, { label: string; background: string; color: string }> = {
  no_identity: {
    label: 'No identity',
    background: 'rgb(245,245,245)',
    color: '#666',
  },
  identity_present_unverified: {
    label: 'Unverified',
    background: 'rgb(255,243,224)',
    color: 'rgb(194,91,18)',
  },
  verified: {
    label: 'Verified',
    background: 'rgb(236,253,243)',
    color: 'rgb(22,101,52)',
  },
  manual_review: {
    label: 'Manual review',
    background: 'rgb(254,243,199)',
    color: 'rgb(146,64,14)',
  },
  revoked_or_blocked: {
    label: 'Blocked',
    background: 'rgb(254,242,242)',
    color: 'rgb(185,28,28)',
  },
};

export function TrustPanel({
  state,
  loading,
  error,
  reason,
  actionLabel = 'Open AadhaarChain',
}: {
  state: PortfolioTrustState;
  loading?: boolean;
  error?: string | null;
  reason?: string | null;
  actionLabel?: string;
}) {
  if (loading) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5 text-sm text-slate-600">
        Loading AadhaarChain trust state…
      </div>
    );
  }

  const meta = STATE_META[state];
  const message =
    error ||
    reason ||
    ({
      no_identity: 'Create an identity anchor in AadhaarChain before using auditable evidence or challenge flows.',
      identity_present_unverified: 'Complete AadhaarChain verification before uploading evidence or filing high-trust challenges.',
      manual_review: 'Verification is under manual review. Evidence-backed actions stay paused until review completes.',
      revoked_or_blocked: 'Trust state is blocked or revoked. Review AadhaarChain before attempting elevated transparency actions.',
      verified: 'Trust state is verified. Evidence and challenge actions can be attributed to a portable trust record.',
    }[state]);

  return (
    <div
      className="rounded-3xl p-5"
      style={{
        backgroundColor: meta.background,
        color: meta.color,
        border: `1px solid ${meta.color}22`,
      }}
    >
      <div className="flex items-center gap-2 text-sm font-semibold">
        <span
          className="inline-block h-2 w-2 rounded-full"
          style={{ backgroundColor: meta.color }}
        />
        AadhaarChain trust: {meta.label}
      </div>
      <p className="mt-2 text-sm">{message}</p>
      <a
        href={`${IDENTITY_URL}/dashboard`}
        className="mt-3 inline-flex text-sm underline"
        style={{ color: meta.color }}
      >
        {actionLabel}
      </a>
    </div>
  );
}
