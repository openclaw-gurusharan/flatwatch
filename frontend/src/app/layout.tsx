import type { Metadata } from "next";
import "./globals.css";
import { SkipLink } from "@/components/a11y";
import { AuthProvider } from "@/lib/auth";
import { WalletProvider } from "@/lib/wallet";

export const metadata: Metadata = {
  title: "FlatWatch - Society Transparency System",
  description: "Financial transparency for housing societies",
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="font-sans">
      <body className="antialiased">
        <WalletProvider>
          <AuthProvider>
            <SkipLink />
            <main id="main-content">
              {children}
            </main>
          </AuthProvider>
        </WalletProvider>
      </body>
    </html>
  );
}
