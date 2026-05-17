param(
    [Parameter(Mandatory = $true)]
    [string]$PaperPath
)

$image = "multi-agent-research"

docker build -t $image .
docker run --rm -v ${PWD}:/workspace -w /workspace $image --paper $PaperPath
