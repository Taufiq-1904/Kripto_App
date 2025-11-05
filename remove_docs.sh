#!/bin/bash
# Simple script to remove documentation files

echo "========================================"
echo "  Remove Documentation Files"
echo "========================================"
echo ""

# Array of files to remove
files=(
    "API_REFERENCE.md"
    "BACKWARD_COMPATIBILITY_FIX.md"
    "BUILD_SUCCESS.md"
    "CHANGELOG.md"
    "DATABASE_ENCRYPTION_GUIDE.md"
    "DOCUMENTATION_GUIDE.md"
    "ENCRYPTION_SUCCESS.md"
    "FACE_RECOGNITION_GUIDE.md"
    "FACE_RECOGNITION_SUCCESS.md"
    "FULL_ENCRYPTION_GUIDE.md"
    "INSTALL_GUIDE.md"
    "TECHNICAL_DOCS.md"
)

echo "Step 1: Remove from git tracking and delete locally..."
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        git rm "$file"
        echo "  Removed: $file"
    fi
done

echo ""
echo "Step 2: Commit changes..."
git commit -m "Remove documentation files - already uploaded to GitHub"

echo ""
echo "Step 3: Push to GitHub..."
git push origin main

echo ""
echo "Done! Documentation files removed from local and GitHub."
