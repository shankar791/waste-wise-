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

export default function ImageSequence() {
    const { viewport } = useThree();
    const meshRef = useRef<THREE.Mesh>(null);
    const [textures, setTextures] = useState<THREE.Texture[]>([]);
    const [loaded, setLoaded] = useState(false);

    // Progress ref to be mutated by GSAP
    const progress = useRef({ value: 0 });

    // Preload textures
    useEffect(() => {
        const manager = new THREE.LoadingManager();
        const loader = new THREE.TextureLoader(manager);
        const tempTextures: THREE.Texture[] = [];

        manager.onLoad = () => {
            setTextures(tempTextures);
            setLoaded(true);
            window.dispatchEvent(new Event("assets-loaded"));
        };

        for (let i = 0; i < TOTAL_FRAMES; i++) {
            tempTextures[i] = loader.load(`${FRAME_PATH}${i}.jpg`);
        }

        return () => {
            // Cleanup textures on unmount
            tempTextures.forEach(t => t.dispose());
        };
    }, []);

    // Setup ScrollTrigger
    useEffect(() => {
        if (!loaded || textures.length === 0) return;

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
    }, [loaded, textures]);

    // Render loop
    useFrame(() => {
        if (!meshRef.current || !loaded || textures.length === 0) return;

        const frameIndex = Math.min(
            TOTAL_FRAMES - 1,
            Math.floor(progress.current.value * TOTAL_FRAMES)
        );

        const currentTexture = textures[frameIndex];
        if (currentTexture) {
            const material = meshRef.current.material as THREE.MeshBasicMaterial;
            if (material.map !== currentTexture) {
                material.map = currentTexture;
                material.needsUpdate = true;
            }
        }
    });

    // Aspect ratio logic
    const textureAspect = useMemo(() => {
        if (textures[0] && textures[0].image) {
            const img = textures[0].image as any; // Cast to bypass strict {} check
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
