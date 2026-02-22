"use client";

import { Canvas } from "@react-three/fiber";
import { Suspense } from "react";
import ImageSequence from "./ImageSequence";

export default function Scene() {
  return (
    <div className="fixed inset-0 z-0 h-screen w-screen bg-black overflow-hidden">
      <Canvas
        camera={{ position: [0, 0, 2], fov: 75 }} // Moved camera closer for better scale accuracy
        gl={{
          antialias: true,
          alpha: true,
          powerPreference: "high-performance"
        }}
        dpr={[1, 2]}
        style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
      >
        <Suspense fallback={null}>
          <ImageSequence />
        </Suspense>
      </Canvas>
    </div>
  );
}
