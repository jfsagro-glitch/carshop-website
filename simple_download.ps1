# Simple script to create photo placeholders
Write-Host "Creating photo placeholders for all cars..." -ForegroundColor Green

$cars = @(
    @{id=1; brand="Lexus"; model="UX"; url="https://drive.google.com/drive/folders/1FR5s24AvCCFwheEODFLvBXko11UaIBwx"},
    @{id=2; brand="KIA"; model="K5 AWD"; url="https://drive.google.com/drive/folders/1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE"},
    @{id=3; brand="KIA"; model="K5"; url="https://drive.google.com/drive/folders/1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67"},
    @{id=4; brand="KIA"; model="K5 GT Line"; url="https://drive.google.com/drive/folders/1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b"},
    @{id=5; brand="Chevrolet"; model="Equinox"; url="https://drive.google.com/drive/folders/1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK"},
    @{id=6; brand="Chevrolet"; model="Equinox AWD"; url="https://drive.google.com/drive/folders/1fFYDIuWwluL7-cLQzgq6deQUzdFGW5XT"},
    @{id=7; brand="Chevrolet"; model="Equinox"; url="https://drive.google.com/drive/folders/1ItE8WnTKXEjK4oxU7i1WJcYFBRfZ3hiB"},
    @{id=8; brand="Chevrolet"; model="Malibu"; url="https://drive.google.com/drive/folders/1QrIeum3tr8F73TqlI3F8bt9j7Wp3exud"},
    @{id=9; brand="Chevrolet"; model="Malibu"; url="https://drive.google.com/drive/folders/1SLPy7kA6U3GHvmaWMCv1aLV1hgJp78ht"},
    @{id=10; brand="Chevrolet"; model="Trax"; url="https://drive.google.com/drive/folders/1AneTIy_JInzve71jMfyHRAaMmdmv0p9e"},
    @{id=11; brand="KIA"; model="Sportage"; url="https://drive.google.com/drive/folders/1fndY8K0rjlF0JbqnNSl7KRF-kvpyfElP"},
    @{id=12; brand="KIA"; model="Sportage"; url="https://drive.google.com/drive/folders/1vI6ngtd-7pS-Q6GZyx3cT1TAbLP02cJ2"},
    @{id=13; brand="KIA"; model="Sportage"; url="https://drive.google.com/drive/folders/1ktbbcV03TNaxOo85hcxdRI12cf48PDlA"},
    @{id=14; brand="Hyundai"; model="Elantra Limited"; url="https://drive.google.com/drive/folders/1T_WJeiasoMStwqfsrrKCQMrqhauDO2HV"},
    @{id=15; brand="Hyundai"; model="Elantra N Line"; url="https://drive.google.com/drive/folders/11m3ri2m9na7jmqV-Zf2gRwhoXTga4Ruo"},
    @{id=16; brand="BMW"; model="3 Series 330XI"; url="https://drive.google.com/drive/folders/1wbbCZ90K5ph9vunmCnuQJTxSx2sqxQ8n"},
    @{id=17; brand="Volkswagen"; model="Passat R-Line"; url="https://drive.google.com/drive/folders/1lts5r3t6ftPayg55mjSHdMbwRBGMoz78"},
    @{id=18; brand="Volkswagen"; model="Jetta 1.4T R-Line"; url="https://drive.google.com/drive/folders/18gkgVMN3UWPXSSVtB73M1SUxj7Sd6BpG"},
    @{id=19; brand="Subaru"; model="XV Crosstrek Premium"; url="https://drive.google.com/drive/folders/1PMVX5wAq0amBEmIotp7DN0Xfvpb1bPHU"},
    @{id=20; brand="KIA"; model="Forte LXS"; url="https://drive.google.com/drive/folders/1PV5UOJxvCIn52_qrxFJdcvcWuiyE3yM4"},
    @{id=21; brand="Honda"; model="Accord Sport SE"; url="https://drive.google.com/drive/folders/1lkew_BKZI_6xKdInzK4JKEpzgRNsHl3H"},
    @{id=22; brand="Toyota"; model="Venza LE"; url="https://drive.google.com/drive/folders/1PpnoOBW5SxQvATGHODbNrDco5SBFXgAc"},
    @{id=23; brand="Mitsubishi"; model="Outlander Sport 2.0 4WD Limited"; url="https://drive.google.com/drive/folders/1bv6Te0NZyRaskQVJ1bYJItgprQMYlbAZ"},
    @{id=24; brand="Mitsubishi"; model="Outlander Sport 2.0 4WD Limited"; url="https://drive.google.com/drive/folders/1P4HH2NfEva269zYtUZsFSfzeQxQfpzYG"},
    @{id=25; brand="Mitsubishi"; model="Eclipse LE Limited 4WD"; url="https://drive.google.com/drive/folders/1u9kNrW8mwUnRMku1O4hjx3bdVHcyCpKI"},
    @{id=26; brand="Mitsubishi"; model="Eclipse ES 4WD"; url="https://drive.google.com/drive/folders/1m4mktjJLI0feWy8EtHAuEBZB5OetMWqg"},
    @{id=27; brand="Audi"; model="A4 Premium Plus 45"; url="https://drive.google.com/drive/folders/1cZ0NU_NfNc8VKCBdRklkQBETifuKhMLe"},
    @{id=28; brand="BMW"; model="X2 Xdrive28I"; url="https://drive.google.com/drive/folders/1G3wdYypzFOTNVuuUFiXwKnXZtu5y5VXl"},
    @{id=29; brand="BMW"; model="X3 Sdrive30I"; url="https://drive.google.com/drive/folders/1dAJ-gcvjwwYCN8kO7wAIFIdCJcjEnRqG"},
    @{id=30; brand="BMW"; model="X3 Sdrive30I"; url="https://drive.google.com/drive/folders/1os_egVR07QtwJMgWaN6SHWNz5ntSiwaO"},
    @{id=31; brand="Audi"; model="Q3 Premium 40"; url="https://drive.google.com/drive/folders/17TPAkN76U8TCT_l81FJbnpHJLyQGcwo2"},
    @{id=32; brand="BMW"; model="X3 Xdrive30I"; url="https://drive.google.com/drive/folders/12IE_Wr0f6VJ3h5wiFnyCQnzYhu8Fxgyu"},
    @{id=33; brand="Audi"; model="Q5 Premium 45"; url="https://drive.google.com/drive/folders/1hmGbI2RO3F72KXOX8EkYXoMq6uHxISgl"}
)

foreach ($car in $cars) {
    $carFolder = "images\car$($car.id)"
    
    # Create a simple placeholder image
    $placeholderContent = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>$($car.brand) $($car.model)</title>
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
        .car-container {
            text-align: center;
            padding: 2rem;
            background: rgba(55, 65, 81, 0.8);
            border-radius: 12px;
            border: 2px solid #6b7280;
        }
        .car-icon {
            font-size: 6rem;
            margin-bottom: 1rem;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
        }
        .car-title {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #f3f4f6;
        }
        .car-subtitle {
            font-size: 1rem;
            color: #9ca3af;
            margin-bottom: 1.5rem;
        }
        .car-badge {
            background: #4b5563;
            color: #f3f4f6;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            display: inline-block;
            font-size: 0.9rem;
            border: 1px solid #6b7280;
        }
        .car-link {
            color: #60a5fa;
            text-decoration: none;
            margin-top: 1rem;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="car-container">
        <div class="car-icon">🚗</div>
        <div class="car-title">$($car.brand) $($car.model)</div>
        <div class="car-subtitle">Click to view real photos</div>
        <div class="car-badge">📸 Photos Available</div>
        <a href="$($car.url)" target="_blank" class="car-link">Open in Google Drive</a>
    </div>
</body>
</html>
"@
    
    # Save as main.jpg
    $placeholderContent | Out-File -FilePath "$carFolder\main.jpg" -Encoding UTF8
    
    Write-Host "Created placeholder for car $($car.id): $($car.brand) $($car.model)"
}

Write-Host ""
Write-Host "All photo placeholders created!" -ForegroundColor Green
Write-Host ""
Write-Host "To download real photos:" -ForegroundColor Yellow
Write-Host "1. Open each Google Drive link in your browser" -ForegroundColor White
Write-Host "2. Download all photos from each folder" -ForegroundColor White
Write-Host "3. Replace the main.jpg files with real JPG images" -ForegroundColor White
Write-Host "4. The website will automatically display real photos" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

