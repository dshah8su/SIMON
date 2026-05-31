# SIMON + ngrok Startup Script
# Starts ngrok, gets the public URL, starts SIMON, then shows a popup with steps.

$SIMON_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$SERVER_SCRIPT  = Join-Path $SIMON_DIR "src\http_mcp_server.py"
$POPUP_SCRIPT   = Join-Path $SIMON_DIR "src\session_popup.py"
$PORT = 8000

Write-Host ""
Write-Host "  Starting SIMON..." -ForegroundColor Cyan
Write-Host ""

# Find ngrok (handles PATH not refreshed after install)
$ngrok = Get-Command ngrok -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if (-not $ngrok) {
    $ngrok = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter "ngrok.exe" -ErrorAction SilentlyContinue |
             Select-Object -First 1 | Select-Object -ExpandProperty FullName
}
if (-not $ngrok) {
    Write-Host "ERROR: ngrok not found. Run: winget install ngrok.ngrok" -ForegroundColor Red
    exit 1
}

# Kill any previous SIMON server instances
Get-Process -Name python -ErrorAction SilentlyContinue | ForEach-Object {
    $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    if ($cmdline -like "*http_mcp_server*") { Stop-Process $_ -Force -ErrorAction SilentlyContinue }
}
Get-Process -Name ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# Start ngrok in background
Write-Host "  Starting ngrok tunnel..." -ForegroundColor Gray
Start-Process $ngrok -ArgumentList "http $PORT" -WindowStyle Hidden

# Wait for ngrok and get public URL
$publicUrl = $null
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    try {
        $tunnels = (Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop).tunnels
        $publicUrl = $tunnels | Where-Object { $_.public_url -like "https://*" } |
                     Select-Object -First 1 -ExpandProperty public_url
        if ($publicUrl) { break }
    } catch {}
}

if (-not $publicUrl) {
    Write-Host "ERROR: Could not get ngrok URL. Check ngrok auth token." -ForegroundColor Red
    exit 1
}

Write-Host "  ngrok URL: $publicUrl" -ForegroundColor Green

# Start SIMON HTTP MCP server with the public URL
Write-Host "  Starting SIMON server..." -ForegroundColor Gray
$env:PYTHONPATH = $SIMON_DIR
Start-Process python -ArgumentList "`"$SERVER_SCRIPT`" --public-url `"$publicUrl`"" -WorkingDirectory $SIMON_DIR -WindowStyle Hidden

Start-Sleep -Seconds 3
Write-Host "  SIMON is ready." -ForegroundColor Green
Write-Host ""

# Launch the popup (blocks until user closes it)
Start-Process python -ArgumentList "`"$POPUP_SCRIPT`"" -WorkingDirectory $SIMON_DIR -Wait

# Cleanup when popup is closed
Write-Host "Stopping servers..." -ForegroundColor Gray
Get-Process -Name ngrok -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name python -ErrorAction SilentlyContinue | ForEach-Object {
    $cmdline = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    if ($cmdline -like "*http_mcp_server*") { Stop-Process $_ -Force -ErrorAction SilentlyContinue }
}
Write-Host "Done." -ForegroundColor Gray
