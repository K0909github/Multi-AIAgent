param(
    [string]$repo = 'https://github.com/yi-ding-cs/LGG',
    [string]$dest = 'external/LGG',
    [string]$generated = 'research/generated_code',
    [string]$branch = '',
    [string]$createBranch = 'integrate/multi-aia-agent'
)

python "${PSScriptRoot}\..\tools\lgg_integration.py" --repo $repo --dest $dest --generated $generated --create-branch $createBranch
