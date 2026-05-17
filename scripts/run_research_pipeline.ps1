param(
    [Parameter(Mandatory = $true)]
    [string]$PaperPath
)

$image = "multi-agent-research"

Write-Host "[1/3] Building Docker image..."
docker build -t $image .

Write-Host "[2/3] Running paper workflow..."
docker run --rm -v ${PWD}:/workspace -w /workspace $image --paper $PaperPath

Write-Host "[3/3] Generated artifacts:"
Get-ChildItem -Path .\research\artifacts -File | Select-Object Name, Length
Get-ChildItem -Path .\research\generated_code -File | Select-Object Name, Length

Write-Host "Next step: open RUNBOOK.md and review research/artifacts/summary.md, hypotheses.md, and final_draft.md."
