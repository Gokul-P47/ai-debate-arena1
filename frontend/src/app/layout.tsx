import type { Metadata } from 'next';
import { Fraunces, Outfit } from 'next/font/google';

import { Footer } from '@/components/layout/Footer';
import { Navbar } from '@/components/layout/Navbar';
import { APP_NAME, APP_TAGLINE } from '@/lib/constants';

import { Providers } from './providers';
import './globals.css';

const display = Fraunces({
  variable: '--font-display',
  subsets: ['latin'],
});

const sans = Outfit({
  variable: '--font-sans-outfit',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: APP_NAME,
  description: APP_TAGLINE,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col font-[family-name:var(--font-sans-outfit)]">
        <Providers>
          <Navbar />
          <main className="flex-1">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
