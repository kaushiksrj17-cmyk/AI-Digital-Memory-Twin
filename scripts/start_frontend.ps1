# ==============================================================================
# ECHO - Start Frontend Client (Windows PowerShell)
# Target Root: D:\ECHO\frontend
# ==============================================================================

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "ECHO - AI Digital Memory Twin (Next.js Frontend)" -ForegroundColor Cyan
Write-Host "Storage Root: D:\ECHO" -ForegroundColor Green
Write-Host "Starting Next.js development server on http://localhost:3000" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

Set-Location -Path "D:\ECHO\frontend"
$env:NODE_OPTIONS = "-r D:/ECHO/frontend/usb-patch.cjs"

# Check if port 3000 is already occupied
$existing = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Notice: Port 3000 is already active (PID: $($existing[0].OwningProcess)). Frontend dev server is already running." -ForegroundColor Green
    exit 0
}

npm.cmd run dev
