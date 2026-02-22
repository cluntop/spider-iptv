# Cloudflare Pages build script (PowerShell version)

Write-Host "=== Starting IPTV Spider build ==="

# 1. Build frontend
Write-Host "\n=== Building frontend ==="
Set-Location frontend

# Install Node.js dependencies
Write-Host "Installing frontend dependencies..."
npm install

# Build frontend
Write-Host "Building frontend application..."
npm run build

# Copy frontend build output to root dist folder
Write-Host "Copying frontend build output..."
Set-Location ..
New-Item -ItemType Directory -Path dist -Force | Out-Null
Get-ChildItem -Path frontend\dist -Recurse | Copy-Item -Destination dist -Force

# 2. Build backend
Write-Host "\n=== Building backend ==="

# Set environment variables to disable lxml source build
$env:LXML_BUILD_NO_EXTENSIONS = 1
$env:STATIC_DEPS = "true"

Write-Host "Setting environment variables:"
Write-Host "LXML_BUILD_NO_EXTENSIONS=$env:LXML_BUILD_NO_EXTENSIONS"
Write-Host "STATIC_DEPS=$env:STATIC_DEPS"

# Create temporary directory
Write-Host "Creating temporary directory..."
New-Item -ItemType Directory -Path temp -Force | Out-Null

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install wheel for precompiled packages
Write-Host "Installing wheel..."
python -m pip install wheel

# Install lxml precompiled package - force binary package
Write-Host "Installing lxml precompiled package..."
python -m pip install lxml==4.9.4 --only-binary=:all: --no-cache-dir

# Check if lxml installed successfully
Write-Host "Checking lxml installation..."
python -c "import lxml; print('lxml version:', lxml.__version__)"

# Install other dependencies
Write-Host "Installing project dependencies..."
python -m pip install -r requirements.txt --no-cache-dir

# Verify installation
Write-Host "Verifying installation..."
python -c "import requests; print('requests version:', requests.__version__)"
python -c "import bs4; print('beautifulsoup4 version:', bs4.__version__)"
python -c "import psutil; print('psutil version:', psutil.__version__)"

# 3. Copy Cloudflare Functions
Write-Host "\n=== Copying Cloudflare Functions ==="
if (Test-Path "functions") {
    New-Item -ItemType Directory -Path "dist\functions" -Force | Out-Null
    Get-ChildItem -Path "functions" -Recurse | Copy-Item -Destination "dist\functions" -Force
} else {
    Write-Host "No functions directory to copy"
}

if (Test-Path "_pages\_headers") {
    Copy-Item -Path "_pages\_headers" -Destination "dist\_headers" -Force
} else {
    Write-Host "No _headers file to copy"
}

if (Test-Path "_pages\_redirects") {
    Copy-Item -Path "_pages\_redirects" -Destination "dist\_redirects" -Force
} else {
    Write-Host "No _redirects file to copy"
}

# 4. Copy necessary backend files
Write-Host "\n=== Copying backend files ==="
New-Item -ItemType Directory -Path "dist\src" -Force | Out-Null
Write-Host "Copying backend code..."
Get-ChildItem -Path "src" -Recurse | Copy-Item -Destination "dist\src" -Force
Copy-Item -Path "main.py" -Destination "dist\main.py" -Force
Copy-Item -Path "requirements.txt" -Destination "dist\requirements.txt" -Force
Copy-Item -Path "README.md" -Destination "dist\README.md" -Force

# 5. Create build info file
Write-Host "\n=== Creating build info ==="
try {
    $frontendVersion = Get-Content frontend\package.json | Select-String "version" | Select-Object -First 1 | ForEach-Object { $_.Line -split '"' | Select-Object -Index 3 }
} catch {
    $frontendVersion = "unknown"
}
try {
    $pythonVersion = python -c "import sys; print(sys.version)"
} catch {
    $pythonVersion = "unknown"
}

$buildInfo = @"
Build completed at: $(Get-Date)
Frontend build: $frontendVersion
Python backend: $pythonVersion
"@
$buildInfo | Out-File -FilePath "dist\BUILD_INFO.txt" -Force

# 6. Clean temporary files
Write-Host "\n=== Cleaning temporary files ==="
Remove-Item -Path temp -Recurse -Force -ErrorAction SilentlyContinue

# 7. Verify build output
Write-Host "\n=== Verifying build output ==="
Write-Host "Build output directory structure:"
gci dist | Format-Table -AutoSize

if (Test-Path "dist\functions") {
    Write-Host "\nCloudflare Functions:"
    gci "dist\functions" -Recurse | Format-Table -AutoSize
}

if (Test-Path "dist\static") {
    Write-Host "\nFrontend static resources:"
    gci "dist\static" -Recurse | Format-Table -AutoSize
}

Write-Host "\n=== Build completed ==="
Write-Host "Build output directory: $(Get-Location)\dist"
Write-Host "\nNext step: Deploy to Cloudflare Pages or other platform"
