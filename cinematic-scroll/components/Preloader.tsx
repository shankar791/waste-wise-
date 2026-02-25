"use client";

import { useEffect, useState } from "react";
import gsap from "gsap";

export default function Preloader() {
    const [loaded, setLoaded] = useState(false);
    const [progress, setProgress] = useState(0);
    const [elapsedTime, setElapsedTime] = useState(0);

    useEffect(() => {
        const onAssetsLoaded = () => {
            setLoaded(true);
        };

        // Listen for custom event from ImageSequence
        window.addEventListener("assets-loaded", onAssetsLoaded);

        // Fallback safety timeout (8s) - faster for better UX
        const timeout = setTimeout(() => {
            if (!loaded) setLoaded(true);
        }, 8000);

        return () => {
            window.removeEventListener("assets-loaded", onAssetsLoaded);
            clearTimeout(timeout);
        };
    }, [loaded]);

    useEffect(() => {
        if (loaded) {
            // Smooth fade out on completion
            gsap.to(".preloader", {
                opacity: 0,
                duration: 0.8,
                ease: "power2.inOut",
                onComplete: () => {
                    document.querySelector(".preloader")?.remove();
                },
            });
        } else {
            // Fake progress animation for visual feedback
            const interval = setInterval(() => {
                setProgress(prev => {
                    const next = prev + Math.random() * 8;
                    return next > 85 ? 85 : next; // Cap at 85% until fully loaded
                });
            }, 400);

            // Track elapsed time
            const timeInterval = setInterval(() => {
                setElapsedTime(t => t + 1);
            }, 1000);

            return () => {
                clearInterval(interval);
                clearInterval(timeInterval);
            };
        }
    }, [loaded]);

    return (
        <div className="preloader fixed inset-0 z-50 flex items-center justify-center bg-black text-white overflow-hidden">
            <style>{`
                @keyframes pulse-logo {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.6; }
                }
                .logo-pulse {
                    animation: pulse-logo 2s ease-in-out infinite;
                }
            `}</style>
            
            <div className="flex flex-col items-center gap-6 max-w-sm">
                {/* WasteWise Logo with pulse effect */}
                <div className="text-5xl logo-pulse">♻️</div>
                
                {/* Product Name */}
                <div className="text-center">
                    <h1 className="text-3xl font-bold tracking-tight mb-2">
                        WasteWise
                    </h1>
                    <p className="text-sm text-gray-400 tracking-wide">
                        A Greener Future
                    </p>
                </div>

                {/* Progress Bar */}
                <div className="w-full max-w-xs mt-4">
                    <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-green-500 to-green-400 transition-all duration-300 ease-out rounded-full shadow-lg"
                            style={{ width: `${loaded ? 100 : progress}%` }}
                        />
                    </div>
                    <p className="text-xs text-gray-500 text-center mt-3">
                        {loaded ? "Ready" : `Loading... ${Math.floor(progress)}%`}
                    </p>
                </div>

                {/* Loading Text */}
                <div className="text-xs text-gray-600 tracking-widest uppercase mt-2">
                    {loaded ? (
                        <span className="text-green-500">✓ Experience Ready</span>
                    ) : (
                        <span>
                            {elapsedTime > 3 && elapsedTime <= 5 && "Loading assets..."}
                            {elapsedTime > 5 && "Almost there..."}
                            {elapsedTime <= 3 && "Initializing..."}
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
}
