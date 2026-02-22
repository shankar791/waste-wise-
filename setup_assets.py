import os
import shutil

# Source directory containing the frames
source_dir = "ezgif-6c18a521ca0e1629-jpg"
# Destination directory in the new Next.js app
dest_dir = "cinematic-scroll/public/frames"

# Create destination directory if it doesn't exist
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

# Get all files from source directory
files = [f for f in os.listdir(source_dir) if f.endswith('.jpg')]
files.sort()  # Ensure they are in order

print(f"Found {len(files)} frames.")

for i, filename in enumerate(files):
    # Construct new filename: frame_0.jpg, frame_1.jpg, etc.
    new_filename = f"frame_{i}.jpg"
    
    src_path = os.path.join(source_dir, filename)
    dest_path = os.path.join(dest_dir, new_filename)
    
    shutil.copy2(src_path, dest_path)
    print(f"Copied {filename} to {new_filename}")

print("Asset setup complete.")
