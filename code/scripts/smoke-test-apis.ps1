$base = if ($env:API_BASE) { $env:API_BASE } else { "http://127.0.0.1:8001/api/v1" }
$headers = @{ "Content-Type" = "application/json"; "X-Device-Id" = "smoke-test-device" }

function Test-Api($name, $path, $body) {
  try {
    $json = $body | ConvertTo-Json -Depth 8 -Compress
    $resp = Invoke-WebRequest -Uri "$base$path" -Method POST -Headers $headers -Body $json -UseBasicParsing -TimeoutSec 60
    $ok = $resp.StatusCode -ge 200 -and $resp.StatusCode -lt 300
    Write-Output ("[PASS] {0} HTTP {1}" -f $name, $resp.StatusCode)
    return $true
  } catch {
    $msg = $_.Exception.Message
    if ($_.Exception.Response) {
      $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
      $msg = $reader.ReadToEnd()
    }
    Write-Output ("[FAIL] {0} {1}" -f $name, $msg)
    return $false
  }
}

$now = Get-Date
$year = $now.Year
$month = $now.Month
$day = $now.Day
$hour = $now.Hour
$minute = $now.Minute

$results = @()

$results += Test-Api "paipan" "/paipan" @{
  name = "测试"; calendarType = "solar"; year = 1990; month = 5; day = 15
  isLeapMonth = $false; hour = 10; minute = 30; gender = 1
}

$results += Test-Api "meihua" "/meihua/divine" @{
  question = "合作能成吗"; method = "number"; calendarType = "solar"; numbers = @(8)
}

$results += Test-Api "liuyao" "/liuyao/divine" @{
  question = "考试能过吗"; method = "number"; calendarType = "solar"; numbers = @(3, 5, 7)
}

$results += Test-Api "qimen" "/qimen/chart" @{
  question = "出行吉凶"; category = "shizhan"; method = "chaibu"; direction = ""
  useTrueSolarTime = $false; longitude = 120; calendarType = "solar"; isLeapMonth = $false
  year = $year; month = $month; day = $day; hour = $hour; minute = $minute; second = 0
}

$results += Test-Api "liuren" "/liuren/chart" @{
  question = "人事吉凶"; category = "shizhan"; castMethod = "both"; jinkouDifen = ""
  guiRenMode = 0; useTrueSolarTime = $false; longitude = 120; calendarType = "solar"
  isLeapMonth = $false; year = $year; month = $month; day = $day; hour = $hour; minute = $minute; second = 0
}

$results += Test-Api "fengshui" "/fengshui/chart" @{
  question = "宅运如何"; method = "bazhai"; scene = "residence"
  birthYear = 1990; gender = 1; sittingMountain = "zi"
}

$results += Test-Api "ziwei" "/ziwei/chart" @{
  name = "测试"; calendarType = "solar"; year = 1990; month = 5; day = 15
  isLeapMonth = $false; hour = 10; minute = 30; gender = 1
  useTrueSolarTime = $false; longitude = 120; targetYear = $year; question = "论事业"
  rules = @{ leapMonthRule = "current_month"; ziHourRule = "split_midnight"; mutagenTable = "nan_pai" }
}

$results += Test-Api "xingming" "/xingming/chart" @{
  name = "测试"; calendarType = "solar"; year = 1990; month = 5; day = 15
  isLeapMonth = $false; hour = 10; minute = 30; gender = 1
  useTrueSolarTime = $true; longitude = 120; latitude = 35; targetYear = $year
  question = "论财运"; rules = @{ school = "guolao_v1"; ziHourRule = "combined"; dayNightRule = "auto" }
}

$results += Test-Api "zhuge" "/utils/zhuge/divine" @{
  chars = "林山冲"; question = "问求职"
}

$results += Test-Api "jiemeng" "/utils/jiemeng/search" @{
  dream = "梦见龙"; limit = 5
}

$results += Test-Api "naming" "/utils/naming/analyze" @{
  surname = "李"; givenName = "明轩"; birth = $null
}

$pass = ($results | Where-Object { $_ }).Count
$fail = ($results | Where-Object { -not $_ }).Count
Write-Output ""
Write-Output ("Summary: {0} passed, {1} failed (base: {2})" -f $pass, $fail, $base)
if ($fail -gt 0) { exit 1 }
