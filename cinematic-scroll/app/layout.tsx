import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "WasteWise — A Greener Future",
  description: "Premium eco-app for waste classification, carbon tracking, and green rewards. Classify waste, track your carbon footprint, and earn rewards for sustainable living.",
  keywords: "waste management, carbon tracking, recycling, eco-friendly, sustainability",
  authors: [{ name: "WasteWise Team" }],
  openGraph: {
    title: "WasteWise — A Greener Future",
    description: "Premium eco-app for waste classification, carbon tracking, and green rewards",
    type: "website",
  },
  themeColor: "#000000",
  viewport: "width=device-width, initial-scale=1.0, viewport-fit=cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="WasteWise" />
        <meta name="format-detection" content="telephone=no" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 180 180'><rect fill='%23000' width='180' height='180'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-size='70' fill='%2322c55e' font-weight='bold'>♻</text></svg>" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
