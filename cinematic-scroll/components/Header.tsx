"use client";

import Link from "next/link";

export default function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-40 flex items-center justify-between p-6">
      {/* Left: WasteWise Logo/Brand */}
      <div className="flex items-center gap-2">
        <span className="text-2xl">♻️</span>
        <span className="text-sm font-bold tracking-widest uppercase text-white opacity-80 hover:opacity-100 transition-opacity">
          WasteWise
        </span>
      </div>

      {/* Right: Dashboard Button */}
      <Link
        href="http://localhost:8000/dashboard.html"
        target="_blank"
        rel="noopener noreferrer"
        className="px-5 py-2 text-xs font-semibold tracking-wide uppercase rounded-full transition-all duration-300"
        style={{
          background: "rgba(255, 255, 255, 0.15)",
          backdropFilter: "blur(30px)",
          border: "1px solid rgba(255, 255, 255, 0.3)",
          color: "rgba(255, 255, 255, 0.8)",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.background = "rgba(255, 255, 255, 0.25)";
          e.currentTarget.style.color = "rgba(255, 255, 255, 1)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.background = "rgba(255, 255, 255, 0.15)";
          e.currentTarget.style.color = "rgba(255, 255, 255, 0.8)";
        }}
      >
        Dashboard
      </Link>
    </header>
  );
}
