# Script to download photos using wget (if available) or provide manual instructions
Write-Host "=== PHOTO DOWNLOAD SCRIPT ===" -ForegroundColor Green
Write-Host ""

# Check if wget is available
try {
    $wgetVersion = wget --version 2>$null
    if ($wgetVersion) {
        Write-Host "wget is available!" -ForegroundColor Green
        $useWget = $true
    } else {
        Write-Host "wget is not available. Using manual download method." -ForegroundColor Yellow
        $useWget = $false
    }
} catch {
    Write-Host "wget is not available. Using manual download method." -ForegroundColor Yellow
    $useWget = $false
}

if ($useWget) {
    Write-Host "Attempting to download photos with wget..." -ForegroundColor Cyan
    
    # Create a simple batch file for wget commands
    $batchContent = @"
@echo off
echo Downloading photos for all cars...
echo.

REM Car 1 - Lexus UX
echo Downloading Car 1: Lexus UX
mkdir images\car1\photos 2>nul
wget -O "images\car1\photos\main.jpg" "https://drive.google.com/uc?export=download&id=1FR5s24AvCCFwheEODFLvBXko11UaIBwx"

REM Car 2 - KIA K5 AWD  
echo Downloading Car 2: KIA K5 AWD
mkdir images\car2\photos 2>nul
wget -O "images\car2\photos\main.jpg" "https://drive.google.com/uc?export=download&id=1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE"

REM Car 3 - KIA K5
echo Downloading Car 3: KIA K5
mkdir images\car3\photos 2>nul
wget -O "images\car3\photos\main.jpg" "https://drive.google.com/uc?export=download&id=1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67"

echo.
echo Download completed!
echo Check the photos folders for downloaded images.
pause
"@
    
    $batchContent | Out-File -FilePath "download_photos.bat" -Encoding ASCII
    Write-Host "Created download_photos.bat file" -ForegroundColor Green
    Write-Host "Run 'download_photos.bat' to download photos" -ForegroundColor Yellow
    
} else {
    Write-Host "=== MANUAL DOWNLOAD INSTRUCTIONS ===" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Since wget is not available, please download photos manually:" -ForegroundColor White
    Write-Host ""
    Write-Host "1. Open each Google Drive link in your browser" -ForegroundColor Cyan
    Write-Host "2. Download all photos from each folder" -ForegroundColor Cyan  
    Write-Host "3. Place them in the corresponding images/car[number]/ folder" -ForegroundColor Cyan
    Write-Host "4. Rename the main photo as 'main.jpg'" -ForegroundColor Cyan
    Write-Host "5. Name other photos as '2.jpg', '3.jpg', etc." -ForegroundColor Cyan
    Write-Host ""
    
    # Show all car links
    $cars = @(
        @{id=1; brand="Lexus"; model="UX"; url="https://drive.google.com/drive/folders/1FR5s24AvCCFwheEODFLvBXko11UaIBwx"},
        @{id=2; brand="KIA"; model="K5 AWD"; url="https://drive.google.com/drive/folders/1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE"},
        @{id=3; brand="KIA"; model="K5"; url="https://drive.google.com/drive/folders/1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67"},
        @{id=4; brand="KIA"; model="K5 GT Line"; url="https://drive.google.com/drive/folders/1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b"},
        @{id=5; brand="Chevrolet"; model="Equinox"; url="https://drive.google.com/drive/folders/1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK"}
    )
    
    Write-Host "=== FIRST 5 CARS (for example) ===" -ForegroundColor Green
    foreach ($car in $cars) {
        Write-Host "Car $($car.id): $($car.brand) $($car.model)" -ForegroundColor White
        Write-Host "  Folder: images/car$($car.id)/" -ForegroundColor Gray
        Write-Host "  Link: $($car.url)" -ForegroundColor Blue
        Write-Host ""
    }
    
    Write-Host "Check DOWNLOAD_INSTRUCTIONS.txt files in each car folder for complete list." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== NEXT STEPS ===" -ForegroundColor Green
Write-Host "1. Download photos using the method above" -ForegroundColor White
Write-Host "2. Update script.js to use real photos instead of placeholders" -ForegroundColor White  
Write-Host "3. Test the website to ensure photos load correctly" -ForegroundColor White
Write-Host ""

