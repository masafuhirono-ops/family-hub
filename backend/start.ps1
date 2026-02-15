# Family Hub バックエンド起動スクリプト
# 使い方: .\start.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# .env を読み込む
if (Test-Path .env) {
    foreach ($line in Get-Content .env) {
        $line = $line.Trim()
        if ($line -eq "") { continue }
        if ($line.StartsWith("#")) { continue }
        $i = $line.IndexOf("=")
        if ($i -gt 0) {
            $key = $line.Substring(0, $i).Trim()
            $val = $line.Substring($i + 1).Trim().Trim('"').Trim("'")
            [Environment]::SetEnvironmentVariable($key, $val, "Process")
        }
    }
}

& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
