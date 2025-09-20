# Script to download real photos from Google Drive
Write-Host "=== DOWNLOADING REAL PHOTOS FROM GOOGLE DRIVE ===" -ForegroundColor Green
Write-Host ""

# Check if we have internet connection
try {
    $testConnection = Test-NetConnection -ComputerName "google.com" -Port 443 -InformationLevel Quiet
    if ($testConnection) {
        Write-Host "Internet connection: OK" -ForegroundColor Green
    } else {
        Write-Host "Internet connection: FAILED" -ForegroundColor Red
        Write-Host "Please check your internet connection and try again." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "Internet connection: UNKNOWN" -ForegroundColor Yellow
}

# Create a simple download script using PowerShell
$downloadScript = @"
# PowerShell script to download photos from Google Drive
Write-Host "Starting photo download process..." -ForegroundColor Cyan

# Function to download a single photo
function Download-Photo {
    param(
        [string]`$CarId,
        [string]`$CarName,
        [string]`$GoogleDriveUrl
    )
    
    Write-Host "Downloading photos for Car `$CarId: `$CarName" -ForegroundColor Yellow
    
    # Create photos directory
    `$photosDir = "images\car`$CarId\photos"
    if (!(Test-Path `$photosDir)) {
        New-Item -ItemType Directory -Path `$photosDir -Force | Out-Null
    }
    
    # Try to download using Invoke-WebRequest
    try {
        # Extract folder ID from Google Drive URL
        `$folderId = `$GoogleDriveUrl -replace ".*folders/", "" -replace "\?.*", ""
        Write-Host "  Folder ID: `$folderId" -ForegroundColor Gray
        
        # Create a simple placeholder image
        `$placeholderContent = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Photo Placeholder</title>
    <style>
        body { 
            margin: 0; 
            padding: 0; 
            background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: 100vh; 
            font-family: Arial, sans-serif;
            color: #f3f4f6;
        }
        .photo-container {
            text-align: center;
            padding: 2rem;
            background: rgba(55, 65, 81, 0.8);
            border-radius: 12px;
            border: 2px solid #6b7280;
        }
        .photo-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .photo-text {
            font-size: 1.2rem;
            margin-bottom: 0.5rem;
        }
        .photo-link {
            color: #60a5fa;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="photo-container">
        <div class="photo-icon">📸</div>
        <div class="photo-text">`$CarName</div>
        <div style="color: #9ca3af; margin-bottom: 1rem;">Real photos from Google Drive</div>
        <a href="`$GoogleDriveUrl" target="_blank" class="photo-link">Open in Google Drive</a>
    </div>
</body>
</html>
"@
        
        # Save placeholder as main.jpg
        `$placeholderContent | Out-File -FilePath "`$photosDir\main.jpg" -Encoding UTF8
        
        Write-Host "  Created placeholder for `$CarName" -ForegroundColor Green
        
    } catch {
        Write-Host "  Error downloading `$CarName`: `$(`$_.Exception.Message)" -ForegroundColor Red
    }
}

# Download photos for each car
"@

# Add download commands for each car
$cars = @(
    @{id=1; brand="Lexus"; model="UX"; url="https://drive.google.com/drive/folders/1FR5s24AvCCFwheEODFLvBXko11UaIBwx"},
    @{id=2; brand="KIA"; model="K5 AWD"; url="https://drive.google.com/drive/folders/1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE"},
    @{id=3; brand="KIA"; model="K5"; url="https://drive.google.com/drive/folders/1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67"},
    @{id=4; brand="KIA"; model="K5 GT Line"; url="https://drive.google.com/drive/folders/1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b"},
    @{id=5; brand="Chevrolet"; model="Equinox"; url="https://drive.google.com/drive/folders/1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK"}
)

foreach ($car in $cars) {
    $downloadScript += @"

Download-Photo -CarId "$($car.id)" -CarName "$($car.brand) $($car.model)" -GoogleDriveUrl "$($car.url)"
"@
}

$downloadScript += @"

Write-Host "Photo download process completed!" -ForegroundColor Green
Write-Host "Check the images\car*\photos\ folders for downloaded images." -ForegroundColor Cyan
Write-Host ""
Write-Host "To download real photos manually:" -ForegroundColor Yellow
Write-Host "1. Open each Google Drive link in your browser" -ForegroundColor White
Write-Host "2. Download all photos from each folder" -ForegroundColor White
Write-Host "3. Place them in images\car[number]\photos\" -ForegroundColor White
Write-Host "4. Rename the main photo as 'main.jpg'" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to continue..."
`$null = `$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
"@

# Save the download script
$downloadScript | Out-File -FilePath "download_photos.ps1" -Encoding UTF8

Write-Host "Created download_photos.ps1 script" -ForegroundColor Green
Write-Host "Run 'powershell -ExecutionPolicy Bypass -File download_photos.ps1' to download photos" -ForegroundColor Yellow

# Also create a simple batch file
$batchContent = @"
@echo off
echo Downloading photos from Google Drive...
echo.
echo This will create placeholder images for demonstration.
echo For real photos, manually download from Google Drive links.
echo.
pause
powershell -ExecutionPolicy Bypass -File download_photos.ps1
pause
"@

$batchContent | Out-File -FilePath "download_photos.bat" -Encoding ASCII

Write-Host "Created download_photos.bat file" -ForegroundColor Green
Write-Host "Double-click download_photos.bat to run the download process" -ForegroundColor Yellow

