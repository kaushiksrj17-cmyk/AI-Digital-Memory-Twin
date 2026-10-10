# ==============================================================================
# ECHO — Execute Comprehensive Test Suite (Windows PowerShell)
# Target Root: D:\ECHO
# ==============================================================================

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Running ECHO Comprehensive Test Suite" -ForegroundColor Cyan
Write-Host "Target Root: D:\ECHO" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan

Set-Location -Path "D:\ECHO"
$env:PYTHONPATH = "D:\ECHO"

Write-Host "`n[1/2] Running Backend Pytest Tests..." -ForegroundColor Yellow
python -m pytest tests/backend/ -v

if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend tests failed!" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nBackend tests passed successfully!" -ForegroundColor Green

Write-Host "`n[2/2] Checking Storage Boundary & Directories..." -ForegroundColor Yellow
$vaultDirs = @(
    "D:\ECHO\storage\originals",
    "D:\ECHO\storage\processed",
    "D:\ECHO\storage\thumbnails",
    "D:\ECHO\storage\temporary",
    "D:\ECHO\storage\exports",
    "D:\ECHO\storage\local",
    "D:\ECHO\storage\voice"
)
foreach ($dir in $vaultDirs) {
    if (Test-Path $dir) {
        Write-Host "Storage directory verified: $dir" -ForegroundColor Green
    } else {
        Write-Host "Storage directory check failed for $dir!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nAll verification checks passed!" -ForegroundColor Cyan
