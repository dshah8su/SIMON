# start_simon_ngrok.ps1
# Starts ngrok + SIMON HTTP MCP server for Claude.ai / Claude desktop
# Usage: powershell -ExecutionPolicy Bypass -File start_simon_ngrok.ps1

$PORT = 8000
$SRC  = Join-Path $PSScriptRoot "src\http_mcp_server.py"

Write-Host ""
Write-Host "Starting ngrok on port $PORT..." -ForegroundColor Cyan
Start-Process -FilePath "ngrok" -ArgumentList "http $PORT" -WindowStyle Normal

Write-Host "Waiting for ngrok to be ready..."
$publicUrl = $null
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    try {
        $tunnels = (Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop).tunnels
        $https   = $tunnels | Where-Object { $_.proto -eq "https" } | Select-Object -First 1
        if ($https) {
            $publicUrl = $https.public_url
            break
        }
    } catch {}
}

if (-not $publicUrl) {
    Write-Host "ERROR: Could not get ngrok URL. Is ngrok installed and authenticated?" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "ngrok is live: $publicUrl" -ForegroundColor Green
Write-Host ""
Write-Host "Add this URL to Claude.ai MCP settings:" -ForegroundColor Yellow
Write-Host "  $publicUrl/sse" -ForegroundColor White
Write-Host ""
Write-Host "Starting SIMON HTTP MCP server..." -ForegroundColor Cyan

python $SRC --public-url $publicUrl
