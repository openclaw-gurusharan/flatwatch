"use client";

import { useState } from "react";
import Link from "next/link";

interface NavItem {
  href: string;
  label: string;
  icon: string;
}

const navItems: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/transactions", label: "Transactions", icon: "💰" },
  { href: "/receipts", label: "Receipts", icon: "🧾" },
  { href: "/challenges", label: "Challenges", icon: "🚩" },
  { href: "/chat", label: "AI Chat", icon: "🤖" },
];

export function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed bottom-4 right-4 z-50 touch-target action-gradient text-white rounded-full shadow-lg"
        aria-label="Toggle navigation"
        aria-expanded={isOpen}
      >
        {isOpen ? "✕" : "☰"}
      </button>

      {/* Mobile navigation overlay */}
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-40 safe-top safe-bottom"
          onClick={() => setIsOpen(false)}
        >
          <nav
            className="absolute bottom-0 left-0 right-0 bg-white rounded-t-3xl shadow-2xl p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-semibold">FlatWatch</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="touch-target text-gray-500"
                aria-label="Close menu"
              >
                ✕
              </button>
            </div>
            <div className="mobile-nav">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className="flex items-center gap-3 p-4 rounded-xl hover:bg-gray-100 touch-target"
                >
                  <span className="text-2xl">{item.icon}</span>
                  <span className="font-medium">{item.label}</span>
                </Link>
              ))}
            </div>
          </nav>
        </div>
      )}

      {/* Desktop navigation */}
      <nav className="hidden md:flex items-center gap-6">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center gap-2 px-4 py-2 rounded-full hover:bg-gray-100 transition-colors"
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </>
  );
}
