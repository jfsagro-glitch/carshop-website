# Create test images for demonstration
$cars = @(
    @{id=1; brand="Lexus"; model="UX"; year=2021},
    @{id=2; brand="KIA"; model="K5 AWD"; year=2021},
    @{id=3; brand="KIA"; model="K5"; year=2021},
    @{id=4; brand="KIA"; model="K5 GT Line"; year=2022},
    @{id=5; brand="Chevrolet"; model="Equinox"; year=2022},
    @{id=6; brand="Chevrolet"; model="Equinox AWD"; year=2022},
    @{id=7; brand="Chevrolet"; model="Equinox"; year=2021},
    @{id=8; brand="Chevrolet"; model="Malibu"; year=2022},
    @{id=9; brand="Chevrolet"; model="Malibu"; year=2022},
    @{id=10; brand="Chevrolet"; model="Trax"; year=2021},
    @{id=11; brand="KIA"; model="Sportage"; year=2022},
    @{id=12; brand="KIA"; model="Sportage"; year=2021},
    @{id=13; brand="KIA"; model="Sportage"; year=2021},
    @{id=14; brand="Hyundai"; model="Elantra Limited"; year=2021},
    @{id=15; brand="Hyundai"; model="Elantra N Line"; year=2022},
    @{id=16; brand="BMW"; model="3 Series 330XI"; year=2021},
    @{id=17; brand="Volkswagen"; model="Passat R-Line"; year=2021},
    @{id=18; brand="Volkswagen"; model="Jetta 1.4T R-Line"; year=2021},
    @{id=19; brand="Subaru"; model="XV Crosstrek Premium"; year=2022},
    @{id=20; brand="KIA"; model="Forte LXS"; year=2021},
    @{id=21; brand="Honda"; model="Accord Sport SE"; year=2022},
    @{id=22; brand="Toyota"; model="Venza LE"; year=2021},
    @{id=23; brand="Mitsubishi"; model="Outlander Sport 2.0 4WD Limited"; year=2022},
    @{id=24; brand="Mitsubishi"; model="Outlander Sport 2.0 4WD Limited"; year=2021},
    @{id=25; brand="Mitsubishi"; model="Eclipse LE Limited 4WD"; year=2021},
    @{id=26; brand="Mitsubishi"; model="Eclipse ES 4WD"; year=2021},
    @{id=27; brand="Audi"; model="A4 Premium Plus 45"; year=2022},
    @{id=28; brand="BMW"; model="X2 Xdrive28I"; year=2021},
    @{id=29; brand="BMW"; model="X3 Sdrive30I"; year=2021},
    @{id=30; brand="BMW"; model="X3 Sdrive30I"; year=2022},
    @{id=31; brand="Audi"; model="Q3 Premium 40"; year=2021},
    @{id=32; brand="BMW"; model="X3 Xdrive30I"; year=2021},
    @{id=33; brand="Audi"; model="Q5 Premium 45"; year=2022}
)

Write-Host "Creating test images for all cars..."

foreach ($car in $cars) {
    $carFolder = "images\car$($car.id)"
    
    # Create a simple HTML test image
    $testImageHtml = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>$($car.year) $($car.brand) $($car.model)</title>
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
    </style>
</head>
<body>
    <div class="car-container">
        <div class="car-icon">🚗</div>
        <div class="car-title">$($car.year) $($car.brand) $($car.model)</div>
        <div class="car-subtitle">Test Image - Click to view real photos</div>
        <div class="car-badge">📸 Photos Available</div>
    </div>
</body>
</html>
"@
    
    # Save as main.jpg (HTML file that looks like an image)
    $testImageHtml | Out-File -FilePath "$carFolder\main.jpg" -Encoding UTF8
    
    Write-Host "Created test image for car $($car.id): $($car.brand) $($car.model)"
}

Write-Host "All test images created!"
Write-Host "Note: These are HTML files named as .jpg for demonstration."
Write-Host "Replace them with real JPG images from Google Drive."

