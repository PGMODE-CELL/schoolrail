# SchoolRail - Quick Start Script
# Run: .\scripts\start_all.ps1

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  SchoolRail Transport Management" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Kill existing processes
Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'serve_prod|main.py' } | ForEach-Object { Stop-Process -Id $_.Id -Force }
Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'main.py' } | ForEach-Object { Stop-Process -Id $_.Id -Force }
Start-Sleep -Seconds 2

Write-Host "Seeding database..." -ForegroundColor Yellow
python "$PSScriptRoot\..\backend\seed_data.py"

Write-Host "Starting Backend (port 3001)..." -ForegroundColor Yellow
$wsh = New-Object -ComObject WScript.Shell
$wsh.Run("cmd /c cd /d `"$PSScriptRoot\..\backend`" && python main.py", 0, $false)
Start-Sleep -Seconds 10

Write-Host "Starting Production Server (port 8080)..." -ForegroundColor Yellow
Start-Process node -ArgumentList "serve_prod.js" -WorkingDirectory "$PSScriptRoot" -WindowStyle Minimized
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  All Services Running!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Parent App: http://localhost:8080/parent/" -ForegroundColor Cyan
Write-Host "  Driver App: http://localhost:8080/driver/" -ForegroundColor Cyan
Write-Host "  API Docs:   http://localhost:8080/api/v1/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Parent:  parent1@schoolrail.com / admin123" -ForegroundColor Yellow
Write-Host "  Driver:  driver1@schoolrail.com / admin123" -ForegroundColor Yellow
Write-Host ""
