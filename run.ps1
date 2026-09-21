$ErrorActionPreference = 'Stop'
$bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$demoPath = Join-Path $PSScriptRoot 'demo.py'

if (Test-Path -LiteralPath $bundledPython) {
    & $bundledPython -X utf8 $demoPath
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -X utf8 $demoPath
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python -X utf8 $demoPath
} else {
    throw 'Python 3.10+ is required. Install Python and run: python demo.py'
}
exit $LASTEXITCODE
