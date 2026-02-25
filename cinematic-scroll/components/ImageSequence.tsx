"use client";

import { useThree, useFrame } from "@react-three/fiber";
import { useEffect, useRef, useState, useMemo } from "react";
import * as THREE from "three";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

// Configuration
const TOTAL_FRAMES = 96;
const FRAME_PATH = "/frames/frame_";
// Load critical frames first for faster initial display
const CRITICAL_FRAMES = [0, 24, 48, 72, 95]; // Key frames for quick preview

export default function ImageSequence() {
    const { viewport } = useThree();
    const meshRef = useRef<THREE.Mesh>(null);
    const [textures, setTextures] = useState<THREE.Texture[]>([]);
    const [loaded, setLoaded] = useState(false);
    const [criticalLoaded, setCriticalLoaded] = useState(false);

    // Progress ref to be mutated by GSAP
    const progress = useRef({ value: 0 });

    // Preload textures with progressive loading strategy
    useEffect(() => {
        const manager = new THREE.LoadingManager();
        const loader = new THREE.TextureLoader(manager);
        const tempTextures: THREE.Texture[] = [];
        let criticalCount = 0;

        // First: Load critical frames immediately
        const criticalManager = new THREE.LoadingManager();
        const criticalLoader = new THREE.TextureLoader(criticalManager);

        criticalManager.onLoad = () => {
            setCriticalLoaded(true);
            // Dispatch early ready event after critical frames load
            setTimeout(() => {
                window.dispatchEvent(new Event("assets-loaded"));
                setLoaded(true);
            }, 500); // Small delay for smoother transition
        };

        // Load critical frames first
        CRITICAL_FRAMES.forEach((frameIndex) => {
            tempTextures[frameIndex] = criticalLoader.load(`${FRAME_PATH}${frameIndex}.jpg`);
        });

        // Then load remaining frames in background
        const loadRemainingFrames = () => {
            for (let i = 0; i < TOTAL_FRAMES; i++) {
                if (!CRITICAL_FRAMES.includes(i)) {
                    tempTextures[i] = loader.load(`${FRAME_PATH}${i}.jpg`);
                }
            }
        };

        // Delay background loading slightly to prioritize critical frames
        const timeoutId = setTimeout(loadRemainingFrames, 100);

        manager.onLoad = () => {
            setTextures(tempTextures);
        };

        return () => {
            clearTimeout(timeoutId);
            // Cleanup textures on unmount
            tempTextures.forEach(t => t && t.dispose());
        };
    }, []);

    // Setup ScrollTrigger after any assets are ready
    useEffect(() => {
        if (!criticalLoaded || textures.length === 0) return;

        const trigger = ScrollTrigger.create({
            trigger: "body",
            start: "top top",
            end: "bottom bottom",
            scrub: 0.5,
            onUpdate: (self: ScrollTrigger) => {
                progress.current.value = self.progress;

                // Dispatch event when scroll reaches the end
                if (self.progress >= 0.98) {
                    console.log("ImageSequence: Progress complete", self.progress);
                    window.dispatchEvent(new Event("scroll-complete"));
                } else {
                    window.dispatchEvent(new Event("scroll-incomplete"));
                }
            },
        });

        return () => {
            trigger.kill();
        };
    }, [criticalLoaded, textures]);

    // Render loop - fallback to nearest loaded frame if current isn't ready
    useFrame(() => {
        if (!meshRef.current || !criticalLoaded || textures.length === 0) return;

        let frameIndex = Math.min(
            TOTAL_FRAMES - 1,
            Math.floor(progress.current.value * TOTAL_FRAMES)
        );

        // Find nearest loaded texture if current frame isn't loaded
        let attempts = 0;
        while (!textures[frameIndex] && attempts < TOTAL_FRAMES) {
            frameIndex = (frameIndex + 1) % TOTAL_FRAMES;
            attempts++;
        }

        const currentTexture = textures[frameIndex];
        if (currentTexture) {
            const material = meshRef.current.material as THREE.MeshBasicMaterial;
            if (material.map !== currentTexture) {
                material.map = currentTexture;
                material.needsUpdate = true;
            }
        }
    });

    // Aspect ratio logic - fallback to first critical frame
    const textureAspect = useMemo(() => {
        const textureToCheck = textures[0] || textures[CRITICAL_FRAMES[0]];
        if (textureToCheck && textureToCheck.image) {
            const img = textureToCheck.image as any;
            return img.width / img.height;
        }
        return 16 / 9;
    }, [textures]);

    const viewportAspect = viewport.width / viewport.height;

    // Default 1x1 plane at origin [0,0,0]
    let scale: [number, number, number] = [viewport.width, viewport.height, 1];

    if (viewportAspect > textureAspect) {
        // Viewport is wider than image: scale to width
        scale = [viewport.width, viewport.width / textureAspect, 1];
    } else {
        // Viewport is taller than image: scale to height
        scale = [viewport.height * textureAspect, viewport.height, 1];
    }

    return (
        <mesh ref={meshRef} scale={scale}>
            <planeGeometry args={[1, 1]} />
            <meshBasicMaterial transparent={true} />
        </mesh>
    );
}
