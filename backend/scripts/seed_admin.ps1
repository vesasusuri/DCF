# Seed admin and demo users in Supabase Auth (Windows-friendly, no Python deps).
# Usage: powershell -ExecutionPolicy Bypass -File backend/scripts/seed_admin.ps1

$ErrorActionPreference = "Stop"

function Get-EnvValue([string]$Name) {
    $line = Get-Content (Join-Path $PSScriptRoot "..\..\.env") | Where-Object { $_ -match "^$Name=" } | Select-Object -First 1
    if (-not $line) { throw "Missing $Name in .env" }
    return ($line -split "=", 2)[1]
}

$supabaseUrl = Get-EnvValue "SUPABASE_URL"
$serviceKey = Get-EnvValue "SUPABASE_SERVICE_ROLE_KEY"
$adminEmail = if ($env:SYSTEM_ADMIN_EMAIL) { $env:SYSTEM_ADMIN_EMAIL } else { Get-EnvValue "SYSTEM_ADMIN_EMAIL" }
$adminPassword = if ($env:SYSTEM_ADMIN_PASSWORD) { $env:SYSTEM_ADMIN_PASSWORD } else { Get-EnvValue "SYSTEM_ADMIN_PASSWORD" }
$userEmail = if ($env:DEMO_USER_EMAIL) { $env:DEMO_USER_EMAIL } else { Get-EnvValue "DEMO_USER_EMAIL" }
$userPassword = if ($env:DEMO_USER_PASSWORD) { $env:DEMO_USER_PASSWORD } else { Get-EnvValue "DEMO_USER_PASSWORD" }

$headers = @{
    apikey         = $serviceKey
    Authorization  = "Bearer $serviceKey"
    "Content-Type" = "application/json"
}

function Find-UserIdByEmail([string]$Email) {
    $page = 1
    while ($true) {
        $response = Invoke-RestMethod -Uri "$supabaseUrl/auth/v1/admin/users?page=$page&per_page=200" -Headers $headers
        foreach ($user in $response.users) {
            if ($user.email -eq $Email) { return $user.id }
        }
        if ($response.users.Count -lt 200) { return $null }
        $page++
    }
}

function Ensure-User([string]$Email, [string]$Password, [string]$Role, [string]$FullName) {
    $body = @{
        email            = $Email
        password         = $Password
        email_confirm    = $true
        user_metadata    = @{ role = $Role; full_name = $FullName }
    } | ConvertTo-Json

    $userId = Find-UserIdByEmail $Email

    if ($userId) {
        Invoke-RestMethod -Uri "$supabaseUrl/auth/v1/admin/users/$userId" -Method PUT -Headers $headers -Body $body | Out-Null
        Write-Host "Updated user: $Email ($Role)"
        return $userId
    }

    $created = Invoke-RestMethod -Uri "$supabaseUrl/auth/v1/admin/users" -Method POST -Headers $headers -Body $body
    Write-Host "Created user: $Email ($Role)"
    return $created.id
}

Ensure-User $adminEmail $adminPassword "admin" "System Admin" | Out-Null
Ensure-User $userEmail $userPassword "user" "Demo User" | Out-Null

Write-Host ""
Write-Host "Seeded accounts:"
Write-Host "  Admin : $adminEmail / $adminPassword"
Write-Host "  User  : $userEmail / $userPassword"
Write-Host ""
Write-Host "Optional: run supabase/auth.sql in the Supabase SQL editor for the profiles table."
