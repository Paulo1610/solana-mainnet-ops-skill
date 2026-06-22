param(
    [switch]$User,
    [string]$Project,
    [string]$Dest,
    [switch]$Agents
)

$ErrorActionPreference = "Stop"

function Show-Usage {
    Write-Host @"
Install Solana Mainnet Ops Skill.

Usage:
  .\install.ps1 -User [-Agents]
  .\install.ps1 -Project "C:\path\to\project" [-Agents]
  .\install.ps1 -Dest "C:\path\to\skills"
"@
}

$configDir = if ($Agents) { ".agents" } else { ".claude" }
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Dest) {
    $skillsRoot = $Dest
} elseif ($Project) {
    $skillsRoot = Join-Path $Project "$configDir\skills"
} elseif ($User) {
    $skillsRoot = Join-Path $HOME "$configDir\skills"
} else {
    $skillsRoot = Join-Path $HOME "$configDir\skills"
}

if (-not (Test-Path $scriptDir)) {
    throw "Cannot resolve script directory."
}

$target = Join-Path $skillsRoot "solana-mainnet-ops"
New-Item -ItemType Directory -Force -Path $target | Out-Null

foreach ($name in @("skill", "scripts", "agents", "commands")) {
    $targetChild = Join-Path $target $name
    if (Test-Path $targetChild) {
        Remove-Item -LiteralPath $targetChild -Recurse -Force
    }
    Copy-Item -LiteralPath (Join-Path $scriptDir $name) -Destination $target -Recurse
}

Write-Host "Installed solana-mainnet-ops skill to $target"
