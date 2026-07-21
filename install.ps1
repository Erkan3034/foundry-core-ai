# =====================================================================
#  Foundry Core AI - Tek Adim Kurulum (Windows)
#
#  Kullanim (PowerShell):
#    powershell -ExecutionPolicy Bypass -File install.ps1
#
#  Secenekler:
#    -PreloadModels   Modelleri kurulum sirasinda indirir (~2-3 GB).
#                     Onerilir: ilk soruda 10+ dakikalik indirme
#                     beklemek yerine kurulumda bir kez beklenir.
#
#  Betik idempotent'tir: yarim kalan kurulumda tekrar calistirilabilir.
# =====================================================================
param(
    [switch]$PreloadModels
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Step($msg)  { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Ok($msg)    { Write-Host "    OK: $msg" -ForegroundColor Green }
function Fail($msg)  { Write-Host "    HATA: $msg" -ForegroundColor Red; exit 1 }

Write-Host "Foundry Core AI kurulumu baslatiliyor..." -ForegroundColor Yellow

# --- 1. Python 3.11+ kontrolu -----------------------------------------
Step "Python kontrol ediliyor"
$py = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $py) {
    Fail "Python bulunamadi. Kurun: winget install Python.Python.3.12  (kurulumda 'Add to PATH' secili olmali), sonra bu betigi yeniden calistirin."
}
$verOut = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$parts = $verOut.Trim().Split('.')
if ([int]$parts[0] -lt 3 -or ([int]$parts[0] -eq 3 -and [int]$parts[1] -lt 11)) {
    Fail "Python $verOut bulundu; en az 3.11 gerekli. Guncelleyin: winget install Python.Python.3.12"
}
Ok "Python $verOut"

# --- 2. Foundry Local CLI kontrolu ------------------------------------
Step "Foundry Local kontrol ediliyor"
$foundry = Get-Command foundry -ErrorAction SilentlyContinue
if ($null -eq $foundry) {
    Write-Host "    Foundry Local bulunamadi, winget ile kuruluyor..." -ForegroundColor Yellow
    winget install --id Microsoft.FoundryLocal --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) {
        Fail "Foundry Local kurulamadi. Elle kurun: winget install Microsoft.FoundryLocal"
    }
    # Ayni oturumda PATH henuz guncellenmemis olabilir
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
    $foundry = Get-Command foundry -ErrorAction SilentlyContinue
    if ($null -eq $foundry) {
        Fail "Foundry Local kuruldu ama PATH'te gorunmuyor. Yeni bir PowerShell penceresi acip betigi yeniden calistirin."
    }
}
Ok "Foundry Local: $(& foundry --version 2>$null | Select-Object -First 1)"

# --- 3. Sanal ortam ----------------------------------------------------
Step "Python sanal ortami hazirlaniyor"
if (-not (Test-Path "$root\venv\Scripts\python.exe")) {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) { Fail "venv olusturulamadi." }
}
Ok "venv hazir"

# --- 4. Bagimliliklar --------------------------------------------------
Step "Bagimliliklar yukleniyor (requirements.lock - sabitlenmis surumler)"
& "$root\venv\Scripts\python.exe" -m pip install --quiet --upgrade pip
& "$root\venv\Scripts\python.exe" -m pip install --quiet -r requirements.lock
if ($LASTEXITCODE -ne 0) {
    Write-Host "    Lock dosyasi uyusmadi, requirements.txt deneniyor..." -ForegroundColor Yellow
    & "$root\venv\Scripts\python.exe" -m pip install --quiet -r requirements.txt
    if ($LASTEXITCODE -ne 0) { Fail "Bagimliliklar yuklenemedi. Internet baglantisini kontrol edin." }
}
Ok "Bagimliliklar yuklendi"

# --- 5. Yapilandirma ---------------------------------------------------
Step "Yapilandirma dosyasi"
if (-not (Test-Path "$root\.env")) {
    Copy-Item "$root\.env.example" "$root\.env"
    Ok ".env olusturuldu (.env.example'dan)"
} else {
    Ok ".env zaten var, dokunulmadi"
}

# --- 6. Kurulum dogrulamasi -------------------------------------------
Step "Kurulum dogrulaniyor (birim testleri)"
& "$root\venv\Scripts\python.exe" -m pytest tests/ -q --tb=no 2>&1 | Select-Object -Last 1
if ($LASTEXITCODE -ne 0) { Fail "Testler basarisiz. Cikti icin: venv\Scripts\python -m pytest tests/" }
Ok "Tum testler gecti"

# --- 7. (Istege bagli) Modelleri onceden indir -------------------------
if ($PreloadModels) {
    Step "Modeller indiriliyor (bir kereliktir, ~2-3 GB surebilir)"
    & "$root\venv\Scripts\python.exe" -c "from rag_engine import RAGEngine; e = RAGEngine(); e.initialize(); e.shutdown(); print('Modeller hazir.')"
    if ($LASTEXITCODE -ne 0) { Fail "Model indirme basarisiz. Diski ve internet baglantisini kontrol edin." }
    Ok "Modeller indirildi ve dogrulandi"
}

# --- Bitti -------------------------------------------------------------
Write-Host ""
Write-Host "=====================================================" -ForegroundColor Green
Write-Host " Kurulum tamamlandi." -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host ""
Write-Host " Baslatmak icin      : start.bat  (veya: python api_server.py)"
Write-Host " Arayuz              : http://localhost:8000"
Write-Host " Belge eklemek icin  : belgeleri documents\ klasorune koyun,"
Write-Host "                       sonra: venv\Scripts\python main.py ingest"
Write-Host ""
Write-Host " Ilk aciliste 'admin' hesabi rastgele parola ile olusturulur"
Write-Host " ve parola konsola/log'a yazilir. Ilk giristen sonra degistirin."
if (-not $PreloadModels) {
    Write-Host ""
    Write-Host " NOT: Modeller henuz indirilmedi; ilk soruda otomatik inecek" -ForegroundColor Yellow
    Write-Host " (~2-3 GB). Simdi indirmek icin: powershell -ExecutionPolicy Bypass -File install.ps1 -PreloadModels" -ForegroundColor Yellow
}
Write-Host ""
