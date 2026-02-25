"use client";

import { useState, useRef } from "react";
import gsap from "gsap";

interface FileUploadProps {
  onFileSelect?: (file: File) => void;
  maxSizeMB?: number;
  acceptedFormats?: string[];
}

interface ValidationError {
  type: "size" | "format" | "none";
  message: string;
}

export default function FileUpload({
  onFileSelect,
  maxSizeMB = 50,
  acceptedFormats = ["jpg", "jpeg", "png", "gif", "webp"],
}: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<ValidationError>({ type: "none", message: "" });
  const fileInputRef = useRef<HTMLInputElement>(null);
  const barRef = useRef<HTMLDivElement>(null);

  /**
   * Validate file before accepting it
   */
  const validateFile = (selectedFile: File): ValidationError => {
    // Check file size
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (selectedFile.size > maxSizeBytes) {
      return {
        type: "size",
        message: `File size exceeds ${maxSizeMB}MB limit. Your file: ${(selectedFile.size / 1024 / 1024).toFixed(2)}MB`,
      };
    }

    // Check file format
    const fileExtension = selectedFile.name.split(".").pop()?.toLowerCase() || "";
    if (!acceptedFormats.includes(fileExtension)) {
      return {
        type: "format",
        message: `File format not supported. Allowed: ${acceptedFormats.join(", ")}`,
      };
    }

    return { type: "none", message: "" };
  };

  /**
   * Handle file change from input
   */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      const validationError = validateFile(selectedFile);

      if (validationError.type !== "none") {
        setError(validationError);
        setFile(null);
        return;
      }

      setError({ type: "none", message: "" });
      setFile(selectedFile);
      onFileSelect?.(selectedFile);
      animateSuccess();
    }
  };

  /**
   * Handle drag over
   */
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  /**
   * Handle drag leave
   */
  const handleDragLeave = () => {
    setIsDragging(false);
  };

  /**
   * Handle drop
   */
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const selectedFile = e.dataTransfer.files[0];
      const validationError = validateFile(selectedFile);

      if (validationError.type !== "none") {
        setError(validationError);
        setFile(null);
        return;
      }

      setError({ type: "none", message: "" });
      setFile(selectedFile);
      onFileSelect?.(selectedFile);
      animateSuccess();
    }
  };

  /**
   * Animate success feedback
   */
  const animateSuccess = () => {
    if (barRef.current) {
      gsap.fromTo(
        barRef.current,
        { scale: 1 },
        { scale: 1.02, duration: 0.2, yoyo: true, repeat: 1, ease: "power2.out" }
      );
    }
  };

  /**
   * Clear file selection
   */
  const handleClearFile = () => {
    setFile(null);
    setError({ type: "none", message: "" });
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="w-full max-w-2xl px-6">
      <div
        ref={barRef}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !file && fileInputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-label="File upload area, drag and drop or click to select"
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            !file && fileInputRef.current?.click();
          }
        }}
        className={`
          group relative w-full h-20 flex items-center px-10 rounded-2xl 
          border transition-all duration-500 cursor-pointer
          ${
            isDragging
              ? "border-white/40 bg-white/10 scale-[1.01]"
              : "border-white/10 bg-white/5 backdrop-blur-xl hover:border-white/20 hover:bg-white/8"
          }
          ${error.type !== "none" ? "border-red-500/50 bg-red-500/5" : ""}
        `}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept={acceptedFormats.map((ext) => `.${ext}`).join(",")}
          aria-hidden="true"
        />

        <div className="flex items-center w-full justify-between">
          <div className="flex items-center gap-4">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center border transition-colors ${
                error.type !== "none"
                  ? "border-red-500/50 bg-red-500/10"
                  : file
                    ? "border-green-500 bg-green-500/10"
                    : "border-white/20"
              }`}
            >
              {error.type !== "none" ? (
                <span className="text-red-500/70 text-xs">!</span>
              ) : file ? (
                <span className="text-green-500 text-xs">✓</span>
              ) : (
                <span className="text-white/20 text-lg">+</span>
              )}
            </div>

            <div className="flex-1">
              <p
                className={`text-sm tracking-wide transition-colors ${
                  error.type !== "none"
                    ? "text-red-500/70"
                    : file
                      ? "text-white"
                      : "text-white/40"
                }`}
              >
                {error.type !== "none"
                  ? error.message
                  : file
                    ? file.name
                    : "Upload a file or drag & drop here..."}
              </p>
              {file && (
                <p className="text-xs text-white/30 mt-1">
                  {(file.size / 1024 / 1024).toFixed(2)}MB
                </p>
              )}
            </div>
          </div>

          {file ? (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleClearFile();
              }}
              className="opacity-100 transition-opacity text-white/40 hover:text-white/70 text-xs uppercase tracking-widest font-bold"
              aria-label="Remove file"
            >
              Clear
            </button>
          ) : (
            <div className="opacity-0 group-hover:opacity-100 transition-opacity text-white/20 text-xs uppercase tracking-widest font-bold">
              Select
            </div>
          )}
        </div>

        {/* Focus Glow */}
        <div className="absolute inset-x-0 -bottom-px h-px bg-gradient-to-r from-transparent via-white/20 to-transparent scale-x-0 group-hover:scale-x-100 transition-transform duration-700" />
      </div>

      {file && error.type === "none" && (
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
