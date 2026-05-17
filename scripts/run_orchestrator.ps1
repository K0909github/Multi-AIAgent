param(
    [string]$paperPath = '',
    [string]$integrateRepo = ''
)

if (-not $paperPath) {
    Write-Error "Please provide -paperPath"
    exit 1
}

#$PY = python executable
$PY = "python"

$cmd = @($PY, 'scripts\orchestrator.py', '--paper', $paperPath)
if ($integrateRepo) { $cmd += @('--integrate-repo', $integrateRepo) }

Write-Host "Running:" ($cmd -join ' ')
& $cmd