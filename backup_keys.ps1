# Automated Backup Script for Master Keys
# Run this daily or after important changes

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "======================================================================"
Write-Host "  MASTER KEY BACKUP UTILITY"
Write-Host "======================================================================"
Write-Host ""

# Define backup locations
$backupLocations = @(
    ".\backups\$timestamp",              # Local backup
    "$env:OneDrive\Kripto_App_Backup\$timestamp"  # Cloud backup (if OneDrive available)
)

# Files to backup
$filesToBackup = @(
    "db_master.key",
    "face_master.key",
    "secure_messenger.db"
)

# Check if files exist
Write-Host "Checking files to backup..."
$missingFiles = @()
foreach ($file in $filesToBackup) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        Write-Host "  ✅ Found: $file ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Missing: $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️  WARNING: Some files are missing!" -ForegroundColor Yellow
    Write-Host "   These files will be skipped in the backup."
    Write-Host ""
}

# Confirm backup
Write-Host ""
Write-Host "Backup will be created in:"
foreach ($location in $backupLocations) {
    Write-Host "  📁 $location"
}
Write-Host ""

$confirm = Read-Host "Continue with backup? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "❌ Backup cancelled." -ForegroundColor Red
    exit
}

# Perform backup
Write-Host ""
Write-Host "Starting backup..."
Write-Host ""

$successCount = 0
foreach ($location in $backupLocations) {
    try {
        # Create backup directory
        if (-not (Test-Path $location)) {
            New-Item -ItemType Directory -Path $location -Force | Out-Null
        }
        
        # Copy files
        $copiedFiles = 0
        foreach ($file in $filesToBackup) {
            if (Test-Path $file) {
                $destination = Join-Path $location $file
                Copy-Item $file $destination -Force
                $copiedFiles++
            }
        }
        
        # Create backup info file
        $infoFile = Join-Path $location "backup_info.txt"
        $infoContent = @"
Backup Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Files Backed Up: $copiedFiles
Source: $scriptDir
Computer: $env:COMPUTERNAME
User: $env:USERNAME

Files:
$(foreach ($file in $filesToBackup) {
    if (Test-Path $file) {
        $size = (Get-Item $file).Length
        "- $file ($size bytes)"
    }
})
"@
        Set-Content -Path $infoFile -Value $infoContent
        
        Write-Host "  ✅ Backup created: $location" -ForegroundColor Green
        Write-Host "     Files: $copiedFiles / $($filesToBackup.Count)" -ForegroundColor Gray
        $successCount++
    }
    catch {
        Write-Host "  ❌ Failed: $location" -ForegroundColor Red
        Write-Host "     Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Summary
Write-Host ""
Write-Host "======================================================================"
Write-Host "  BACKUP SUMMARY"
Write-Host "======================================================================"
Write-Host ""

if ($successCount -gt 0) {
    Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
    Write-Host "   Backup locations: $successCount / $($backupLocations.Count)" -ForegroundColor Green
    Write-Host "   Timestamp: $timestamp" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📝 IMPORTANT REMINDERS:" -ForegroundColor Yellow
    Write-Host "   1. Test restore regularly (monthly)" -ForegroundColor Yellow
    Write-Host "   2. Keep backup locations secure" -ForegroundColor Yellow
    Write-Host "   3. Don't share master keys" -ForegroundColor Yellow
    Write-Host "   4. If keys are lost, data CANNOT be recovered" -ForegroundColor Yellow
} else {
    Write-Host "❌ Backup FAILED!" -ForegroundColor Red
    Write-Host "   No backups were created successfully." -ForegroundColor Red
    Write-Host "   Please check the errors above." -ForegroundColor Red
}

Write-Host ""
Write-Host "======================================================================"
Write-Host ""

# List recent backups
Write-Host "Recent backups:"
if (Test-Path ".\backups") {
    Get-ChildItem ".\backups" -Directory | 
        Sort-Object LastWriteTime -Descending | 
        Select-Object -First 5 | 
        ForEach-Object {
            $backupSize = (Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum).Sum
            $backupSizeMB = [math]::Round($backupSize / 1MB, 2)
            Write-Host "  📦 $($_.Name) ($backupSizeMB MB)" -ForegroundColor Cyan
        }
} else {
    Write-Host "  (No backups found)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
