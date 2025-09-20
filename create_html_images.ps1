# Create HTML pages with embedded SVG images for each car
$cars = @(
    @{id=1; brand="Lexus"; model="UX"; folderId="1FR5s24AvCCFwheEODFLvBXko11UaIBwx"},
    @{id=2; brand="KIA"; model="K5 AWD"; folderId="1vnofqhi60SeZPumd6qTSg2Z1zcqUi7SE"},
    @{id=3; brand="KIA"; model="K5"; folderId="1cxKqcrwCT3Thfbg_7xBaK-IbCpXbfJ67"},
    @{id=4; brand="KIA"; model="K5 GT Line"; folderId="1o8lInW7TKO72m27HWOxpJAhoK6NxAz7b"},
    @{id=5; brand="Chevrolet"; model="Equinox"; folderId="1Hf_3NXGoBhXKrAQ8Be6COWo6eqNNm0gK"},
    @{id=6; brand="Chevrolet"; model="Equinox AWD"; folderId="1fFYDIuWwluL7-cLQzgq6deQUzdFGW5XT"},
    @{id=7; brand="Chevrolet"; model="Equinox"; folderId="1ItE8WnTKXEjK4oxU7i1WJcYFBRfZ3hiB"},
    @{id=8; brand="Chevrolet"; model="Malibu"; folderId="1QrIeum3tr8F73TqlI3F8bt9j7Wp3exud"},
    @{id=9; brand="Chevrolet"; model="Malibu"; folderId="1SLPy7kA6U3GHvmaWMCv1aLV1hgJp78ht"},
    @{id=10; brand="Chevrolet"; model="Trax"; folderId="1AneTIy_JInzve71jMfyHRAaMmdmv0p9e"},
    @{id=11; brand="KIA"; model="Sportage"; folderId="1fndY8K0rjlF0JbqnNSl7KRF-kvpyfElP"},
    @{id=12; brand="KIA"; model="Sportage"; folderId="1vI6ngtd-7pS-Q6GZyx3cT1TAbLP02cJ2"},
    @{id=13; brand="KIA"; model="Sportage"; folderId="1ktbbcV03TNaxOo85hcxdRI12cf48PDlA"},
    @{id=14; brand="Hyundai"; model="Elantra Limited"; folderId="1T_WJeiasoMStwqfsrrKCQMrqhauDO2HV"},
    @{id=15; brand="Hyundai"; model="Elantra N Line"; folderId="11m3ri2m9na7jmqV-Zf2gRwhoXTga4Ruo"},
    @{id=16; brand="BMW"; model="3 Series 330XI"; folderId="1wbbCZ90K5ph9vunmCnuQJTxSx2sqxQ8n"},
    @{id=17; brand="Volkswagen"; model="Passat R-Line"; folderId="1lts5r3t6ftPayg55mjSHdMbwRBGMoz78"},
    @{id=18; brand="Volkswagen"; model="Jetta 1.4T R-Line"; folderId="18gkgVMN3UWPXSSVtB73M1SUxj7Sd6BpG"},
    @{id=19; brand="Subaru"; model="XV Crosstrek Premium"; folderId="1PMVX5wAq0amBEmIotp7DN0Xfvpb1bPHU"},
    @{id=20; brand="KIA"; model="Forte LXS"; folderId="1PV5UOJxvCIn52_qrxFJdcvcWuiyE3yM4"},
    @{id=21; brand="Honda"; model="Accord Sport SE"; folderId="1lkew_BKZI_6xKdInzK4JKEpzgRNsHl3H"},
    @{id=22; brand="Toyota"; model="Venza LE"; folderId="1PpnoOBW5SxQvATGHODbNrDco5SBFXgAc"},
    @{id=23; brand="Mitsubishi"; model="Outlander Sport 2.0 4WD Limited"; folderId="1bv6Te0NZyRaskQVJ1bYJItgprQMYlbAZ"},
    @{id=24; brand="Mitsubishi"; model="Outlander Sport 2.0 4WD Limited"; folderId="1P4HH2NfEva269zYtUZsFSfzeQxQfpzYG"},
    @{id=25; brand="Mitsubishi"; model="Eclipse LE Limited 4WD"; folderId="1u9kNrW8mwUnRMku1O4hjx3bdVHcyCpKI"},
    @{id=26; brand="Mitsubishi"; model="Eclipse ES 4WD"; folderId="1m4mktjJLI0feWy8EtHAuEBZB5OetMWqg"},
    @{id=27; brand="Audi"; model="A4 Premium Plus 45"; folderId="1cZ0NU_NfNc8VKCBdRklkQBETifuKhMLe"},
    @{id=28; brand="BMW"; model="X2 Xdrive28I"; folderId="1G3wdYypzFOTNVuuUFiXwKnXZtu5y5VXl"},
    @{id=29; brand="BMW"; model="X3 Sdrive30I"; folderId="1dAJ-gcvjwwYCN8kO7wAIFIdCJcjEnRqG"},
    @{id=30; brand="BMW"; model="X3 Sdrive30I"; folderId="1os_egVR07QtwJMgWaN6SHWNz5ntSiwaO"},
    @{id=31; brand="Audi"; model="Q3 Premium 40"; folderId="17TPAkN76U8TCT_l81FJbnpHJLyQGcwo2"},
    @{id=32; brand="BMW"; model="X3 Xdrive30I"; folderId="12IE_Wr0f6VJ3h5wiFnyCQnzYhu8Fxgyu"},
    @{id=33; brand="Audi"; model="Q5 Premium 45"; folderId="1hmGbI2RO3F72KXOX8EkYXoMq6uHxISgl"}
)

foreach ($car in $cars) {
    $carFolder = "images\car$($car.id)"
    
    # Create HTML page with embedded SVG
    $htmlContent = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>$($car.brand) $($car.model)</title>
    <style>
        body { 
            margin: 0; 
            padding: 0; 
            background: #374151; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: 100vh; 
            font-family: Arial, sans-serif;
        }
        .car-container {
            text-align: center;
            color: #f3f4f6;
        }
        .car-svg {
            width: 100%;
            height: auto;
            max-width: 800px;
        }
        .car-info {
            margin-top: 1rem;
            font-size: 1.2rem;
            font-weight: bold;
        }
        .car-subtitle {
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: #9ca3af;
        }
    </style>
</head>
<body>
    <div class="car-container">
        <svg class="car-svg" viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#374151;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#4b5563;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#bg)"/>
            <g transform="translate(400, 200)">
                <circle cx="0" cy="0" r="80" fill="#6b7280" opacity="0.3"/>
                <path d="M-60,-20 L60,-20 L50,20 L-50,20 Z" fill="#9ca3af" opacity="0.6"/>
                <rect x="-40" y="-10" width="80" height="20" fill="#d1d5db" opacity="0.8"/>
                <circle cx="-25" cy="25" r="15" fill="#6b7280"/>
                <circle cx="25" cy="25" r="15" fill="#6b7280"/>
            </g>
            <text x="400" y="450" text-anchor="middle" fill="#f3f4f6" font-family="Arial, sans-serif" font-size="24" font-weight="bold">$($car.brand) $($car.model)</text>
            <text x="400" y="480" text-anchor="middle" fill="#9ca3af" font-family="Arial, sans-serif" font-size="16">Click to view photos</text>
        </svg>
        <div class="car-info">$($car.brand) $($car.model)</div>
        <div class="car-subtitle">Click to view photos</div>
    </div>
</body>
</html>
"@
    
    $htmlContent | Out-File -FilePath "$carFolder\image.html" -Encoding UTF8
    
    Write-Host "Created HTML image for car $($car.id): $($car.brand) $($car.model)"
}

Write-Host "All HTML images created!"

