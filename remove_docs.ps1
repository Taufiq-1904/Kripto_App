# Remove Documentation Files Script
# Script untuk menghapus file dokumentasi dari lokal dan GitHub

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Remove Documentation Files" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# List of documentation files to remove
$docFiles = @(
    "API_REFERENCE.md",
    "BACKWARD_COMPATIBILITY_FIX.md",
    "BUILD_SUCCESS.md",
    "CHANGELOG.md",
    "DATABASE_ENCRYPTION_GUIDE.md",
    "DOCUMENTATION_GUIDE.md",
    "ENCRYPTION_SUCCESS.md",
    "FACE_RECOGNITION_GUIDE.md",
    "FACE_RECOGNITION_SUCCESS.md",
    "FULL_ENCRYPTION_GUIDE.md",
    "INSTALL_GUIDE.md",
    "TECHNICAL_DOCS.md"
)

Write-Host "Files to be removed:" -ForegroundColor Yellow
foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Write-Host "  [EXISTS] $file" -ForegroundColor Green
    } else {
        Write-Host "  [NOT FOUND] $file" -ForegroundColor Gray
    }
}
Write-Host ""

# Confirm deletion
$confirm = Read-Host "Do you want to remove these files? (yes/no)"
if ($confirm -ne "yes" -and $confirm -ne "y") {
    Write-Host "Operation cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Step 1: Removing files locally..." -ForegroundColor Cyan

$removedCount = 0
foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  Removed: $file" -ForegroundColor Green
        $removedCount++
    }
}

Write-Host "  Total files removed: $removedCount" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Git operations..." -ForegroundColor Cyan

# Check git status
Write-Host "  Checking git status..." -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "Step 3: Staging deletions for commit..." -ForegroundColor Cyan
foreach ($file in $docFiles) {
    git rm --cached $file 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Staged for deletion: $file" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Step 4: Committing changes..." -ForegroundColor Cyan
git commit -m "Remove documentation files - already uploaded to GitHub"

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Commit successful!" -ForegroundColor Green
} else {
    Write-Host "  Commit failed or no changes to commit" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 5: Pushing to GitHub..." -ForegroundColor Cyan
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Push successful!" -ForegroundColor Green
} else {
    Write-Host "  Push failed!" -ForegroundColor Red
    Write-Host "  Please check your connection and try: git push origin main" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Operation Complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  - Local files removed: $removedCount" -ForegroundColor White
Write-Host "  - Git commit: Done" -ForegroundColor White
Write-Host "  - GitHub push: Check above for status" -ForegroundColor White
Write-Host ""
Write-Host "Note: README.md was kept (not removed)" -ForegroundColor Gray
Write-Host ""
