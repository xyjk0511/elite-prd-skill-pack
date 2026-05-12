param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

$ErrorActionPreference = "Stop"

$skillsDir = Join-Path $Root ".agents\skills"
if (-not (Test-Path -LiteralPath $skillsDir)) {
    throw "Missing skills directory: $skillsDir"
}

$skills = Get-ChildItem -LiteralPath $skillsDir -Directory
if (-not $skills) {
    throw "No skills found under: $skillsDir"
}

foreach ($skill in $skills) {
    $skillFile = Join-Path $skill.FullName "SKILL.md"
    if (-not (Test-Path -LiteralPath $skillFile)) {
        throw "Missing SKILL.md for $($skill.Name)"
    }

    $content = Get-Content -LiteralPath $skillFile -Raw
    if ($content -notmatch "(?s)^---\s*.*?\bname:\s*.+?\bdescription:\s*.+?---") {
        throw "Invalid frontmatter in $skillFile"
    }

    Write-Host "Valid: $($skill.Name)"
}

Write-Host "All skills valid."
