import FileUpload from "@/components/FileUpload";
import Link from "next/link";

export default function UploadPage() {
    return (
        <main className="min-h-screen w-full bg-[#050505] flex flex-col items-center justify-center relative overflow-hidden">
            {/* Background radial glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-white/[0.02] rounded-full blur-[120px] pointer-events-none" />

            <div className="relative z-10 flex flex-col items-center text-center animate-in fade-in duration-1000">
                <h1 className="text-4xl md:text-5xl font-light tracking-tight text-white mb-4">
                    Share your contribution.
                </h1>
                <p className="text-white/40 text-sm max-w-sm mb-16 font-light leading-relaxed">
                    Upload your data to help us build a more sustainable and transparent environment.
                </p>

                <FileUpload />

                <Link
                    href="/"
                    className="mt-20 text-[10px] uppercase tracking-[0.5em] text-white/20 hover:text-white transition-colors"
                >
                    ← Return to journey
                </Link>
            </div>

            {/* Footer deco */}
            <div className="absolute bottom-10 text-[9px] uppercase tracking-[1em] text-white/5 pointer-events-none">
                Sustainability Flow v1.0
            </div>
        </main>
    );
}
