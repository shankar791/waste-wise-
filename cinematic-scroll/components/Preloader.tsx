"use client";

import { useEffect, useState } from "react";
import gsap from "gsap";

export default function Preloader() {
    const [loaded, setLoaded] = useState(false);
    const [progress, setProgress] = useState(0);

    useEffect(() => {
        const onAssetsLoaded = () => {
            setLoaded(true);
        };

        // Listen for custom event from ImageSequence
        window.addEventListener("assets-loaded", onAssetsLoaded);

        // Fallback safety timeout (10s)
        const timeout = setTimeout(() => {
            if (!loaded) setLoaded(true);
        }, 10000);

        return () => {
            window.removeEventListener("assets-loaded", onAssetsLoaded);
            clearTimeout(timeout);
        };
    }, [loaded]);

    useEffect(() => {
        if (loaded) {
            gsap.to(".preloader", {
                opacity: 0,
                duration: 1,
                ease: "power2.inOut",
                onComplete: () => {
                    document.querySelector(".preloader")?.remove();
                },
            });
        } else {
            // Fake progress animation for visual feedback
            const interval = setInterval(() => {
                setProgress(prev => {
                    const next = prev + Math.random() * 10;
                    return next > 90 ? 90 : next;
                });
            }, 500);
            return () => clearInterval(interval);
        }
    }, [loaded]);

    return (
        <div className="preloader fixed inset-0 z-50 flex items-center justify-center bg-black text-white">
            <div className="flex flex-col items-center gap-4">
                <div className="text-2xl font-bold tracking-widest uppercase">
                    Loading Experience
                </div>
                <div className="w-64 h-1 bg-gray-800 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-white transition-all duration-300 ease-out"
                        style={{ width: `${loaded ? 100 : progress}%` }}
                    />
                </div>
            </div>
        </div>
    );
}
