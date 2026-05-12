param(
    [string]$CodexHome = $env:CODEX_HOME,
    [switch]$SkipFeatureEnable
)

$ErrorActionPreference = "Stop"

if (-not $CodexHome) {
    $CodexHome = Join-Path $HOME ".codex"
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$sourceSkills = Join-Path $repoRoot ".agents\skills"
$targetSkills = Join-Path $CodexHome "skills"

if (-not (Test-Path -LiteralPath $sourceSkills)) {
    throw "Skill source directory not found: $sourceSkills"
}

New-Item -ItemType Directory -Force -Path $targetSkills | Out-Null

$skills = Get-ChildItem -LiteralPath $sourceSkills -Directory
foreach ($skill in $skills) {
    $target = Join-Path $targetSkills $skill.Name
    if (Test-Path -LiteralPath $target) {
        Remove-Item -LiteralPath $target -Recurse -Force
    }
    Copy-Item -LiteralPath $skill.FullName -Destination $target -Recurse
    Write-Host "Installed $($skill.Name) -> $target"
}

if (-not $SkipFeatureEnable) {
    $codex = Get-Command codex -ErrorAction SilentlyContinue
    if ($codex) {
        Write-Host "Enabling Codex native choice UI feature..."
        & codex features enable default_mode_request_user_input | Write-Host
    } else {
        Write-Warning "codex CLI not found. Enable native choice UI manually: codex features enable default_mode_request_user_input"
    }
}

& (Join-Path $PSScriptRoot "validate.ps1") -Root $repoRoot
Write-Host "Install complete."
