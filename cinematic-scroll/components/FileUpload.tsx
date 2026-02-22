"use client";

import { useState, useRef } from "react";
import gsap from "gsap";

export default function FileUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const barRef = useRef<HTMLDivElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            animateSuccess();
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
            animateSuccess();
        }
    };

    const animateSuccess = () => {
        gsap.fromTo(
            barRef.current,
            { scale: 1 },
            { scale: 1.02, duration: 0.2, yoyo: true, repeat: 1, ease: "power2.out" }
        );
    };

    return (
        <div className="w-full max-w-2xl px-6">
            <div
                ref={barRef}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`
          group relative w-full h-20 flex items-center px-10 rounded-2xl cursor-pointer
          border border-white/10 bg-white/5 backdrop-blur-xl transition-all duration-500
          ${isDragging ? "border-white/40 bg-white/10 scale-[1.01]" : "hover:border-white/20 hover:bg-white/8"}
        `}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    className="hidden"
                />

                <div className="flex items-center w-full justify-between">
                    <div className="flex items-center gap-4">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center border transition-colors ${file ? 'border-green-500 bg-green-500/10' : 'border-white/20'}`}>
                            {file ? (
                                <span className="text-green-500 text-xs">✓</span>
                            ) : (
                                <span className="text-white/20 text-lg">+</span>
                            )}
                        </div>

                        <p className={`text-sm tracking-wide transition-colors ${file ? 'text-white' : 'text-white/40'}`}>
                            {file ? file.name : "Upload a file or drag & drop here..."}
                        </p>
                    </div>

                    <div className="opacity-0 group-hover:opacity-100 transition-opacity text-white/20 text-xs uppercase tracking-widest font-bold">
                        Select
                    </div>
                </div>

                {/* Focus Glow */}
                <div className="absolute inset-x-0 -bottom-px h-px bg-gradient-to-r from-transparent via-white/20 to-transparent scale-x-0 group-hover:scale-x-100 transition-transform duration-700" />
            </div>

            {file && (
                <div className="mt-8 flex items-center justify-center gap-6 animate-in fade-in slide-in-from-bottom-4 duration-1000">
                    <div className="h-px flex-1 bg-white/5" />
                    <p className="text-[10px] text-white/30 uppercase tracking-[0.4em] font-medium">
                        File ready for processing
                    </p>
                    <div className="h-px flex-1 bg-white/5" />
                </div>
            )}
        </div>
    );
}
