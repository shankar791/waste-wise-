"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

export default function CTASection() {
    const [isVisible, setIsVisible] = useState(false);
    const sectionRef = useRef<HTMLDivElement>(null);
    const router = useRouter();

    useEffect(() => {
        const handleComplete = () => {
            setIsVisible(true);
        };
        const handleIncomplete = () => {
            setIsVisible(false);
        };

        window.addEventListener("scroll-complete", handleComplete);
        window.addEventListener("scroll-incomplete", handleIncomplete);

        return () => {
            window.removeEventListener("scroll-complete", handleComplete);
            window.removeEventListener("scroll-incomplete", handleIncomplete);
        };
    }, []);

    return (
        <div
            ref={sectionRef}
            style={{
                position: "fixed",
                inset: 0,
                zIndex: 50,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                backgroundColor: "rgba(0,0,0,0.85)",
                backdropFilter: "blur(12px)",
                transition: "opacity 1s ease, visibility 1s ease",
                opacity: isVisible ? 1 : 0,
                visibility: isVisible ? "visible" : "hidden",
                pointerEvents: isVisible ? "auto" : "none",
            }}
        >
            <div
                style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    textAlign: "center",
                    padding: "0 2rem",
                    transform: isVisible ? "translateY(0)" : "translateY(60px)",
                    transition: "transform 1.2s cubic-bezier(0.16, 1, 0.3, 1)",
                    transitionDelay: "0.3s",
                }}
            >
                <h2
                    style={{
                        fontSize: "clamp(2.5rem, 8vw, 7rem)",
                        fontWeight: 900,
                        letterSpacing: "-0.04em",
                        color: "white",
                        textTransform: "uppercase",
                        lineHeight: 0.9,
                        marginBottom: "3rem",
                    }}
                >
                    SUSTAINABLE
                    <br />
                    ENVIRONMENT
                </h2>

                <button
                    onClick={() => window.location.href = "/home.html"}
                    style={{
                        padding: "1.2rem 3rem",
                        backgroundColor: "white",
                        color: "black",
                        fontWeight: 700,
                        textTransform: "uppercase",
                        letterSpacing: "0.2em",
                        fontSize: "0.8rem",
                        borderRadius: "9999px",
                        border: "none",
                        cursor: "pointer",
                        transform: isVisible ? "scale(1)" : "scale(0.9)",
                        transition: "transform 1s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease",
                        transitionDelay: "0.6s",
                        boxShadow: "0 0 0px rgba(255,255,255,0)",
                    }}
                    onMouseEnter={(e) => {
                        (e.target as HTMLButtonElement).style.boxShadow =
                            "0 0 40px rgba(255,255,255,0.3)";
                    }}
                    onMouseLeave={(e) => {
                        (e.target as HTMLButtonElement).style.boxShadow =
                            "0 0 0px rgba(255,255,255,0)";
                    }}
                >
                    Get Started
                </button>

                <p
                    style={{
                        marginTop: "2rem",
                        color: "rgba(255,255,255,0.3)",
                        fontSize: "0.65rem",
                        textTransform: "uppercase",
                        letterSpacing: "0.4em",
                    }}
                >
                    The journey begins here
                </p>
            </div>
        </div>
    );
}
