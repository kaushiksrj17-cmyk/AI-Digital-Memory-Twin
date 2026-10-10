import './globals.css';
import type { Metadata } from 'next';
import { AppShell } from '@/components/AppShell';

export const metadata: Metadata = {
  title: 'ECHO — AI Digital Memory Twin',
  description:
    'Evidence-Grounded, Privacy-Preserving Multimodal AI for Interactive Digital Memory Preservation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
