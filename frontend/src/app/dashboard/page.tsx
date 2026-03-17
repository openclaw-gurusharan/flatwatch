// Dashboard page - Shame Dashboard for FlatWatch
'use client';

import { useEffect, useState } from 'react';
import { PageLayout } from '@/components/layout/PageLayout';
import { FinancialSummary } from '@/components/dashboard/FinancialSummary';
import { TransactionList } from '@/components/dashboard/TransactionList';
import { TrustPanel } from '@/components/trust/TrustPanel';
import { ProtectedRoute } from '@/lib/ProtectedRoute';
import { transactionsApi, type Transaction } from '@/lib/api';
import { useTrustState } from '@/lib/useTrustState';
import { useWallet } from '@solana/wallet-adapter-react';

interface Summary {
  balance: number;
  total_inflow: number;
  total_outflow: number;
  unmatched_transactions: number;
  recent_transactions_24h: number;
}

function DashboardContent() {
  const { publicKey } = useWallet();
  const trust = useTrustState(publicKey?.toBase58() ?? null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    try {
      setError(null);
      const summaryData = await transactionsApi.getSummary();
      setSummary(summaryData);
      const txns = await transactionsApi.list({ limit: 10 });
      setTransactions(txns);
      setLoading(false);
    } catch {
      setError('Failed to load data');
      setLoading(false);
    }
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      void loadData();
    }, 0);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, []);

  const handleSync = async () => {
    try {
      await transactionsApi.sync();
      await loadData();
    } catch {
      setError('Sync failed');
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 animate-pulse rounded-full bg-[rgb(255,97,26)]" />
          <span className="text-[#999]">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-white">
        <div className="text-center">
          <p className="text-[rgb(255,97,26)]">{error}</p>
          <button
            onClick={loadData}
            className="mt-4 inline-flex h-12 items-center justify-center rounded-full bg-[rgb(255,97,26)] px-6 font-medium text-white shadow-[0_2px_8px_rgba(255,97,26,0.3)] transition-all hover:shadow-[0_4px_12px_rgba(255,97,26,0.4)] active:scale-95"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <PageLayout title="FlatWatch" description="">
      <TrustPanel
        state={trust.state}
        loading={trust.loading}
        error={trust.error}
        reason={trust.reason}
        actionLabel="Review trust in AadhaarChain"
      />

      {/* Sync Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSync}
          className="h-10 rounded-full bg-[rgb(238,238,238)] px-4 text-sm font-medium text-[#333] transition-all hover:bg-[rgb(232,232,232)] active:scale-95"
        >
          Sync Now
        </button>
      </div>

      {/* Financial Summary */}
      {summary && (
        <FinancialSummary
          balance={summary.balance}
          totalInflow={summary.total_inflow}
          totalOutflow={summary.total_outflow}
          unmatched={summary.unmatched_transactions}
          recent={summary.recent_transactions_24h}
        />
      )}

      {/* Transaction List */}
      <TransactionList transactions={transactions} />

      {/* Footer status */}
      <div className="flex items-center justify-center gap-2 rounded-full bg-[rgb(238,238,238)] px-4 py-3">
        <span className="h-2 w-2 rounded-full bg-[rgb(76,175,80)]" />
        <span className="text-sm text-[#999]">System online</span>
      </div>
    </PageLayout>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
