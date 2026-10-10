# ==============================================================================
# ECHO - Start Backend Server (Windows PowerShell)
# Target Root: D:\ECHO
# ==============================================================================

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "ECHO - AI Digital Memory Twin (Backend Server)" -ForegroundColor Cyan
Write-Host "Storage Root: D:\ECHO" -ForegroundColor Green
Write-Host "Starting FastAPI server on http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "API Health Check: http://127.0.0.1:8000/api/v1/health" -ForegroundColor Yellow
Write-Host "Root Health Check: http://127.0.0.1:8000/health" -ForegroundColor Yellow
Write-Host "OpenAPI Docs: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

Set-Location -Path "D:\ECHO"
$env:PYTHONPATH = "D:\ECHO"

# Check if port 8000 is already occupied
$existing = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Notice: Port 8000 is already active (PID: $($existing[0].OwningProcess)). Backend is already running." -ForegroundColor Green
    exit 0
}

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
