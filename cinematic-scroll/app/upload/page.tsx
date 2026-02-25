"use client";

import { useState, useEffect } from "react";
import FileUpload from "@/components/FileUpload";
import Link from "next/link";

interface UploadResponse {
  success: boolean;
  waste_type: string;
  subcategory: string;
  recyclable_status: string;
  energy_potential: string;
  recommended_treatment: string;
  disposal_instructions: string;
  carbon_saved: number;
  trees_equivalent: number;
  sustainability_score: number;
  reward_points: number;
  impact_message: string;
}

interface ValidationError {
  field: string;
  message: string;
}

export default function UploadPage() {
  const [email, setEmail] = useState("");
  const [weight, setWeight] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [uploadError, setUploadError] = useState("");
  const [showResult, setShowResult] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  /**
   * Load email from session storage
   */
  useEffect(() => {
    const savedEmail = sessionStorage.getItem("userEmail");
    if (savedEmail) {
      setEmail(savedEmail);
    }
  }, []);

  /**
   * Validate form inputs
   */
  const validateForm = (): boolean => {
    const newErrors: ValidationError[] = [];

    if (!email || email.trim() === "") {
      newErrors.push({ field: "email", message: "Please log in to upload waste" });
    }

    if (!weight || parseFloat(weight) <= 0) {
      newErrors.push({ field: "weight", message: "Weight must be greater than 0" });
    } else if (parseFloat(weight) > 1000) {
      newErrors.push({ field: "weight", message: "Weight cannot exceed 1000 kg" });
    }

    if (!file) {
      newErrors.push({ field: "file", message: "Please select a file" });
    }

    setErrors(newErrors);
    return newErrors.length === 0;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm() || !file) {
      return;
    }

    setIsLoading(true);
    setUploadError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("email", email);
      formData.append("weight", weight);
      formData.append("image", file);

      const response = await fetch(`${API_URL}/user/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || `Upload failed with status ${response.status}`
        );
      }

      const data: UploadResponse = await response.json();
      setResult(data);
      setShowResult(true);

      // Reset form after successful upload
      setTimeout(() => {
        setWeight("");
        setFile(null);
      }, 2000);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Failed to upload file";
      setUploadError(errorMessage);
      console.error("Upload error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle file selection from FileUpload component
   */
  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    // Clear file error when user selects a new file
    setErrors((prev) => prev.filter((e) => e.field !== "file"));
  };

  const getErrorMessage = (field: string) => {
    return errors.find((e) => e.field === field)?.message;
  };

  return (
    <main className="min-h-screen w-full bg-[#050505] flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background radial glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-white/[0.02] rounded-full blur-[120px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-2xl px-4 flex flex-col items-center text-center">
        {!showResult ? (
          <>
            <h1 className="text-4xl md:text-5xl font-light tracking-tight text-white mb-4">
              Share your contribution.
            </h1>
            <p className="text-white/40 text-sm max-w-sm mb-12 font-light leading-relaxed">
              Upload your waste to help us build a more sustainable and
              transparent environment.
            </p>

            <form onSubmit={handleSubmit} className="w-full space-y-8">
              {/* Email Display */}
              <div className="space-y-2">
                <label className="block text-xs uppercase tracking-widest text-white/50">
                  Logged in as
                </label>
                {email ? (
                  <p className="text-sm text-white font-medium">{email}</p>
                ) : (
                  <p className="text-sm text-red-500">
                    <Link href="/" className="underline hover:text-red-400">
                      Please log in first
                    </Link>
                  </p>
                )}
              </div>

              {/* Weight Input */}
              <div className="space-y-2">
                <label
                  htmlFor="weight"
                  className="block text-xs uppercase tracking-widest text-white/50"
                >
                  Waste Weight (kg)
                </label>
                <input
                  id="weight"
                  type="number"
                  step="0.01"
                  min="0"
                  max="1000"
                  value={weight}
                  onChange={(e) => {
                    setWeight(e.target.value);
                    setErrors((prev) =>
                      prev.filter((err) => err.field !== "weight")
                    );
                  }}
                  placeholder="Enter weight in kilograms"
                  className={`
                    w-full px-4 py-3 rounded-xl bg-white/5 border backdrop-blur-xl
                    text-white placeholder-white/20 outline-none transition-all
                    ${
                      getErrorMessage("weight")
                        ? "border-red-500/50 focus:border-red-500/70"
                        : "border-white/10 focus:border-white/30"
                    }
                  `}
                  aria-invalid={!!getErrorMessage("weight")}
                  aria-describedby={
                    getErrorMessage("weight") ? "weight-error" : undefined
                  }
                />
                {getErrorMessage("weight") && (
                  <p
                    id="weight-error"
                    className="text-xs text-red-500/70 mt-1"
                  >
                    {getErrorMessage("weight")}
                  </p>
                )}
              </div>

              {/* File Upload Component */}
              <FileUpload onFileSelect={handleFileSelect} maxSizeMB={50} />

              {/* Error Display */}
              {uploadError && (
                <div
                  className="px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30"
                  role="alert"
                >
                  <p className="text-sm text-red-500/80">{uploadError}</p>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading || !email || !weight || !file}
                className={`
                  w-full py-3 px-6 rounded-xl font-medium text-sm uppercase tracking-wider
                  transition-all duration-300
                  ${
                    isLoading || !email || !weight || !file
                      ? "bg-white/5 text-white/30 cursor-not-allowed"
                      : "bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 text-white hover:border-green-500/50 hover:from-green-500/30 hover:to-emerald-500/30"
                  }
                `}
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="inline-block w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Analyzing...
                  </span>
                ) : (
                  "Analyze & Upload"
                )}
              </button>
            </form>

            <Link
              href="/"
              className="mt-12 text-[10px] uppercase tracking-[0.5em] text-white/20 hover:text-white transition-colors"
            >
              ← Return to journey
            </Link>
          </>
        ) : result ? (
          /* Success Result Display */
          <div className="space-y-8 animate-in fade-in duration-500">
            <div className="space-y-3">
              <h2 className="text-3xl md:text-4xl font-light text-white">
                Analysis Complete
              </h2>
              <p className="text-green-500/80 font-medium">
                {result.impact_message}
              </p>
            </div>

            {/* Results Grid */}
            <div className="grid grid-cols-2 gap-4 md:gap-6">
              <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xl">
                <p className="text-xs text-white/50 uppercase tracking-wider mb-2">
                  Waste Type
                </p>
                <p className="text-lg font-medium text-white capitalize">
                  {result.waste_type}
                </p>
                <p className="text-xs text-white/40 mt-1">
                  {result.subcategory}
                </p>
              </div>

              <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xl">
                <p className="text-xs text-white/50 uppercase tracking-wider mb-2">
                  Carbon Saved
                </p>
                <p className="text-lg font-medium text-white">
                  {result.carbon_saved} kg
                </p>
              </div>

              <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xl">
                <p className="text-xs text-white/50 uppercase tracking-wider mb-2">
                  Trees Equivalent
                </p>
                <p className="text-lg font-medium text-white">
                  {result.trees_equivalent} trees
                </p>
              </div>

              <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xl">
                <p className="text-xs text-white/50 uppercase tracking-wider mb-2">
                  Reward Points
                </p>
                <p className="text-lg font-medium text-emerald-400">
                  +{result.reward_points} pts
                </p>
              </div>
            </div>

            {/* Disposal Information */}
            <div className="space-y-3 p-6 rounded-xl bg-white/5 border border-white/10 backdrop-blur-xl text-left">
              <h3 className="text-sm font-medium text-white uppercase tracking-wider">
                Disposal Guide
              </h3>
              <div className="space-y-2 text-sm text-white/70">
                <p>
                  <span className="text-white/50">Status:</span>{" "}
                  <span className="capitalize">{result.recyclable_status}</span>
                </p>
                <p>
                  <span className="text-white/50">Treatment:</span>{" "}
                  <span className="capitalize">{result.recommended_treatment}</span>
                </p>
                <p>
                  <span className="text-white/50">Instructions:</span>{" "}
                  {result.disposal_instructions}
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-4 pt-4">
              <button
                onClick={() => {
                  setShowResult(false);
                  setResult(null);
                  setWeight("");
                  setFile(null);
                }}
                className="py-3 px-6 rounded-xl font-medium text-sm uppercase tracking-wider text-white bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 hover:border-green-500/50 transition-all"
              >
                Upload Another
              </button>
              <Link
                href="/"
                className="py-3 px-6 rounded-xl font-medium text-sm uppercase tracking-wider text-white/40 hover:text-white transition-colors"
              >
                Back to Dashboard
              </Link>
            </div>
          </div>
        ) : null}
      </div>

      {/* Footer deco */}
      <div className="absolute bottom-10 text-[9px] uppercase tracking-[1em] text-white/5 pointer-events-none">
        Sustainability Flow v1.0
      </div>
    </main>
  );
}
