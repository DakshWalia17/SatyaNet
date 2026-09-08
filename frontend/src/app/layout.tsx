/**
 * Root Layout — Minimal wrapper for all routes.
 * Specific layouts (dashboard sidebar vs. auth pages) are defined in route groups.
 * Developer: Daksh Walia, B.Tech AIML, CGC Mohali
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AIMD | Cyber Cell",
  description: "AI Media Investigation, Detection & Origin Tracing Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} antialiased`}>
        {children}
      </body>
    </html>
  );
}
