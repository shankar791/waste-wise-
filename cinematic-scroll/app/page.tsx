import Scene from "@/components/Scene";
import Preloader from "@/components/Preloader";
import CTASection from "@/components/CTASection";
import Header from "@/components/Header";

export default function Home() {
  return (
    <main className="relative w-full">
      <Header />
      <Preloader />
      <Scene />
      <CTASection />

      {/* Scroll Spacer to provide height for ScrollTrigger */}
      <div style={{ height: "500vh" }} />
    </main>
  );
}
