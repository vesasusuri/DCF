# Idempotent Portfolio Manager seed for Supabase (Windows).
# Usage: powershell -ExecutionPolicy Bypass -File backend/scripts/seed_portfolio_manager.ps1

$ErrorActionPreference = "Stop"

function Get-EnvValue([string]$Name, [string]$Default = "") {
    $envPath = Join-Path $PSScriptRoot "..\..\.env"
    $line = Get-Content $envPath | Where-Object { $_ -match "^$Name=" } | Select-Object -First 1
    if (-not $line) {
        if ($Default) { return $Default }
        throw "Missing $Name in .env"
    }
    return ($line -split "=", 2)[1].Trim()
}

$supabaseUrl = Get-EnvValue "SUPABASE_URL"
$serviceKey = Get-EnvValue "SUPABASE_SERVICE_ROLE_KEY"
$pmEmail = if ($env:PORTFOLIO_MANAGER_EMAIL) { $env:PORTFOLIO_MANAGER_EMAIL } else { Get-EnvValue "PORTFOLIO_MANAGER_EMAIL" "pm@example.com" }
$pmPassword = if ($env:PORTFOLIO_MANAGER_PASSWORD) { $env:PORTFOLIO_MANAGER_PASSWORD } else { Get-EnvValue "PORTFOLIO_MANAGER_PASSWORD" "Pm1234!" }
$pmFullName = if ($env:PORTFOLIO_MANAGER_FULL_NAME) { $env:PORTFOLIO_MANAGER_FULL_NAME } else { "Portfolio Manager" }
$roleValue = "portfolio_manager"

$headers = @{
    apikey         = $serviceKey
    Authorization  = "Bearer $serviceKey"
    "Content-Type" = "application/json"
}

Write-Host "INFO [portfolio-manager-seed] Starting Portfolio Manager startup seed"
Write-Host "INFO [portfolio-manager-seed] Email: $pmEmail"
Write-Host "INFO [portfolio-manager-seed] Role: PORTFOLIO_MANAGER (stored as $roleValue)"

function Find-UserIdByEmail([string]$Email) {
    $page = 1
    while ($true) {
        Write-Host "INFO [portfolio-manager-seed] Checking Supabase Auth — GET /auth/v1/admin/users?page=$page&per_page=200"
        $response = Invoke-RestMethod -Uri "$supabaseUrl/auth/v1/admin/users?page=$page&per_page=200" -Headers $headers
        foreach ($user in $response.users) {
            if ($user.email -eq $Email) {
                Write-Host "INFO [portfolio-manager-seed] Auth user already exists: $Email (id=$($user.id))"
                return $user.id
            }
        }
        if ($response.users.Count -lt 200) { return $null }
        $page++
    }
}

function Get-Profile([string]$UserId) {
    Write-Host "INFO [portfolio-manager-seed] Checking public.profiles — GET /rest/v1/profiles?id=eq.$UserId"
    $profileHeaders = $headers.Clone()
    $profileHeaders["Accept"] = "application/json"
    $profiles = Invoke-RestMethod -Uri "$supabaseUrl/rest/v1/profiles?id=eq.$UserId&select=id,email,full_name,role" -Headers $profileHeaders
    if ($profiles -and $profiles.Count -gt 0) {
        $profile = $profiles[0]
        Write-Host "INFO [portfolio-manager-seed] Application profile already exists: email=$($profile.email) role=$($profile.role)"
        return $profile
    }
    Write-Host "INFO [portfolio-manager-seed] Application profile not found for user id=$UserId"
    return $null
}

function Ensure-Profile([string]$UserId, [string]$Email, [string]$FullName) {
    $existing = Get-Profile $UserId
    if ($existing -and $existing.email -eq $Email -and $existing.full_name -eq $FullName -and $existing.role -eq $roleValue) {
        Write-Host "INFO [portfolio-manager-seed] SUCCESS: Application profile already up to date (no write needed)"
        return
    }

  $profileBody = @{
        id        = $UserId
        email     = $Email
        full_name = $FullName
        role      = $roleValue
    } | ConvertTo-Json

    $upsertHeaders = $headers.Clone()
    $upsertHeaders["Prefer"] = "resolution=merge-duplicates"
    if ($existing) {
        Write-Host "INFO [portfolio-manager-seed] Updating application profile — POST /rest/v1/profiles (upsert)"
    } else {
        Write-Host "INFO [portfolio-manager-seed] Creating application profile — POST /rest/v1/profiles (upsert)"
    }
    Invoke-RestMethod -Uri "$supabaseUrl/rest/v1/profiles" -Method POST -Headers $upsertHeaders -Body $profileBody | Out-Null
    Write-Host "INFO [portfolio-manager-seed] SUCCESS: Application profile upserted"
}

try {
    $userId = Find-UserIdByEmail $pmEmail
    $authBody = @{
        email         = $pmEmail
        password      = $pmPassword
        email_confirm = $true
        user_metadata = @{ role = $roleValue; full_name = $pmFullName }
    } | ConvertTo-Json

    if ($userId) {
        Write-Host "INFO [portfolio-manager-seed] Updating auth user — PUT /auth/v1/admin/users/$userId"
        Invoke-RestMethod -Uri "$supabaseUrl/auth/v1/admin/users/$userId" -Method PUT -Headers $headers -Body $authBody | Out-Null
        Write-Host "INFO [portfolio-manager-seed] SUCCESS: Auth user updated ($pmEmail)"
    } else {
        Write-Host "INFO [portfolio-manager-seed] Creating auth user — POST /auth/v1/admin/users"
        $created = Invoke-RestMethod -Uri "$supabaseUrl/auth/v1/admin/users" -Method POST -Headers $headers -Body $authBody
        $userId = $created.id
        Write-Host "INFO [portfolio-manager-seed] SUCCESS: Auth user created ($pmEmail, id=$userId)"
    }

    Ensure-Profile $userId $pmEmail $pmFullName
    Write-Host "INFO [portfolio-manager-seed] Portfolio Manager seed completed successfully"
    Write-Host "INFO [portfolio-manager-seed] Login: $pmEmail / $pmPassword"
}
catch {
    Write-Host "ERROR [portfolio-manager-seed] FAILED: $_"
    exit 1
}
