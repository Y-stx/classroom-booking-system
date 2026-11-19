# =====================================================================
# Classroom Reservation System - Smoke Test Script
# PowerShell version of chapter8-smoke.sh
# Usage: powershell -ExecutionPolicy Bypass -File .\scripts\smoke-test.ps1
# =====================================================================

$BASE = 'http://localhost:8080/api'
$script:PASS = 0
$script:FAIL = 0

function Write-Check($name, $success, $detail) {
    if ($success) {
        Write-Host "[PASS] $name - $detail" -ForegroundColor Green
        $script:PASS++
    } else {
        Write-Host "[FAIL] $name - $detail" -ForegroundColor Red
        $script:FAIL++
    }
}

Write-Host '============================================'
Write-Host ' Classroom Reservation System - Smoke Test'
Write-Host '============================================'
Write-Host ''

# --- Check 1: Backend service running ---
try {
    $health = Invoke-RestMethod -Uri "$BASE/dashboard/stats" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Check 'Backend Service' $true 'Port 8080 responding'
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 401) {
        Write-Check 'Backend Service' $true 'Port 8080 responding (401 = not logged in)'
    } else {
        Write-Check 'Backend Service' $false 'Port 8080 not responding'
        exit 1
    }
}

# --- Login to get Token ---
$loginBody = @{ username = 'admin'; password = 'admin123' } | ConvertTo-Json
try {
    $loginRes = Invoke-RestMethod -Uri "$BASE/auth/login" -Method POST -ContentType 'application/json' -Body $loginBody
    $TOKEN = $loginRes.data.token
    Write-Check 'Admin Login' $true 'Token obtained'
} catch {
    Write-Check 'Admin Login' $false 'Login failed'
    exit 1
}

$HEADERS = @{ Authorization = "Bearer $TOKEN" }

# --- Check 2: Pagination query ---
try {
    $res = Invoke-RestMethod -Uri "$BASE/classrooms?page=1&pageSize=10" -Method GET -Headers $HEADERS
    $total = $res.data.total
    Write-Check 'Classroom Pagination' ($total -gt 0) "Returned $total classrooms"
} catch {
    Write-Check 'Classroom Pagination' $false 'Query failed'
}

# --- Check 2b: Status filter ---
try {
    $res = Invoke-RestMethod -Uri "$BASE/classrooms?page=1&pageSize=10&status=AVAILABLE" -Method GET -Headers $HEADERS
    $allAvailable = $res.data.list | Where-Object { $_.status -ne 'AVAILABLE' }
    $isCorrect = (@($allAvailable)).Count -eq 0
    Write-Check 'Status Filter' $isCorrect 'All results are AVAILABLE'
} catch {
    Write-Check 'Status Filter' $false 'Filter failed'
}

# --- Check 3: Illegal operation blocked (K4) ---
# Backend returns HTTP 200 with body {code:400, success:false} for business errors
try {
    $res = Invoke-RestMethod -Uri "$BASE/approvals/4/approve" -Method POST -Headers $HEADERS
    $blocked = (-not $res.success) -and ($res.code -eq 400)
    Write-Check 'Illegal Approval Block' $blocked "Correctly rejected: $($res.message)"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Check 'Illegal Approval Block' ($statusCode -eq 400) "Correctly rejected (HTTP $statusCode)"
}

# --- Check 3b: Time conflict detection ---
try {
    $conflictBody = @{
        classroomId = 1
        title = 'Conflict Test'
        startTime = '2026-09-08 09:00:00'
        endTime = '2026-09-08 09:30:00'
    } | ConvertTo-Json
    $res = Invoke-RestMethod -Uri "$BASE/reservations" -Method POST -ContentType 'application/json' -Headers $HEADERS -Body $conflictBody
    $blocked = (-not $res.success) -and ($res.code -eq 400)
    Write-Check 'Time Conflict Detection' $blocked "Correctly rejected: $($res.message)"
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    Write-Check 'Time Conflict Detection' ($statusCode -eq 400) "Correctly rejected (HTTP $statusCode)"
}

# --- Check 4: Dashboard stats ---
try {
    $res = Invoke-RestMethod -Uri "$BASE/dashboard/stats" -Method GET -Headers $HEADERS
    $hasData = $res.data.totalClassrooms -gt 0 -and $res.data.totalUsers -gt 0
    $detail = "Classrooms=$($res.data.totalClassrooms) Users=$($res.data.totalUsers) Reservations=$($res.data.totalReservations)"
    Write-Check 'Dashboard Stats' $hasData $detail
} catch {
    Write-Check 'Dashboard Stats' $false 'Stats API failed'
}

# --- Check 5: Approval center ---
try {
    $res = Invoke-RestMethod -Uri "$BASE/approvals/pending?page=1&pageSize=10" -Method GET -Headers $HEADERS
    Write-Check 'Approval Center' $true "Pending: $($res.data.total)"
} catch {
    Write-Check 'Approval Center' $false 'Failed to get pending list'
}

# --- Check 6: Usage log list ---
try {
    $res = Invoke-RestMethod -Uri "$BASE/usage/list?page=1&pageSize=10" -Method GET -Headers $HEADERS
    Write-Check 'Usage Log' $true "Records: $($res.data.total)"
} catch {
    Write-Check 'Usage Log' $false 'Failed to get usage logs'
}

Write-Host ''
Write-Host '============================================'
$passCount = $script:PASS
$failCount = $script:FAIL
Write-Host " Smoke Test Result: PASS=$passCount  FAIL=$failCount"
Write-Host '============================================'

if ($failCount -gt 0) {
    exit 1
} else {
    Write-Host 'All checks passed!' -ForegroundColor Green
}
