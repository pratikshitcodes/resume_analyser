$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\frontend"
npm run dev -- --host 127.0.0.1 --port 5173
