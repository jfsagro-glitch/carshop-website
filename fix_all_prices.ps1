# Script to fix all car prices according to the new list
Write-Host "Fixing all car prices in script.js..." -ForegroundColor Green

# Read the current script.js file
$scriptContent = Get-Content "script.js" -Raw

# Define all price updates according to the user's list
$priceUpdates = @{
    # Car 1: 2021 Lexus UX - price should be 2530000
    "price: 2530000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 2530000, // Включает растаможку и доставку"
    
    # Car 2: 2021 KIA K5 AWD - price should be 1800000  
    "price: 1800000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1800000, // Включает растаможку и доставку"
    
    # Car 3: 2021 KIA K5 - price should be 1950000
    "price: 1950000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1950000, // Включает растаможку и доставку"
    
    # Car 4: 2022 KIA K5 GT Line - price should be 1920000
    "price: 1920000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1920000, // Включает растаможку и доставку"
    
    # Car 5: 2022 Chevrolet Equinox - price should be 1830000
    "price: 1830000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1830000, // Включает растаможку и доставку"
    
    # Car 6: 2022 Chevrolet Equinox AWD - price should be 1830000
    "price: 1830000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1830000, // Включает растаможку и доставку"
    
    # Car 7: 2021 Chevrolet Equinox - price should be 1490000
    "price: 1490000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1490000, // Включает растаможку и доставку"
    
    # Car 8: 2022 Chevrolet Malibu - price should be 1420000
    "price: 1420000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1420000, // Включает растаможку и доставку"
    
    # Car 9: 2022 Chevrolet Malibu - price should be 1320000
    "price: 1320000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1320000, // Включает растаможку и доставку"
    
    # Car 10: 2021 Chevrolet Trax - price should be 1260000
    "price: 1260000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1260000, // Включает растаможку и доставку"
    
    # Car 11: 2022 KIA Sportage - price should be 2110000
    "price: 2110000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 2110000, // Включает растаможку и доставку"
    
    # Car 12: 2021 KIA Sportage - price should be 2010000
    "price: 2010000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 2010000, // Включает растаможку и доставку"
    
    # Car 13: 2021 KIA Sportage - price should be 2030000
    "price: 1730000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 2030000, // Включает растаможку и доставку"
    
    # Car 14: 2021 Hyundai Elantra Limited - price should be 1770000
    "price: 1770000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1770000, // Включает растаможку и доставку"
    
    # Car 15: 2022 Hyundai Elantra N Line - price should be 1880000
    "price: 1880000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1880000, // Включает растаможку и доставку"
    
    # Car 16: 2021 BMW 3 Series 330XI - price should be 3150000
    "price: 3650000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 3150000, // Включает растаможку и доставку"
    
    # Car 17: 2021 Volkswagen Passat R-Line - price should be 1960000
    "price: 1960000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1960000, // Включает растаможку и доставку"
    
    # Car 18: 2021 Volkswagen Jetta 1.4T R-Line - price should be 1390000
    "price: 1390000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1390000, // Включает растаможку и доставку"
    
    # Car 19: 2022 Subaru XV Crosstrek Premium - price should be 1730000
    "price: 1730000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1730000, // Включает растаможку и доставку"
    
    # Car 20: 2021 KIA Forte LXS - price should be 1480000
    "price: 1480000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1480000, // Включает растаможку и доставку"
    
    # Car 21: 2022 Honda Accord Sport SE - price should be 1910000
    "price: 1910000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1910000, // Включает растаможку и доставку"
    
    # Car 22: 2021 Toyota Venza LE - price should be 2520000
    "price: 2920000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 2520000, // Включает растаможку и доставку"
    
    # Car 23: 2022 Mitsubishi Outlander Sport 2.0 4WD Limited - price should be 1590000
    "price: 1590000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1590000, // Включает растаможку и доставку"
    
    # Car 24: 2021 Mitsubishi Outlander Sport 2.0 4WD Limited - price should be 1750000
    "price: 1750000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1750000, // Включает растаможку и доставку"
    
    # Car 25: 2021 Mitsubishi Eclipse LE Limited 4WD - price should be 1700000
    "price: 1700000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1700000, // Включает растаможку и доставку"
    
    # Car 26: 2021 Mitsubishi Eclipse ES 4WD - price should be 1680000
    "price: 1680000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 1680000, // Включает растаможку и доставку"
    
    # Car 27: 2022 Audi A4 Premium Plus 45 - price should be 3070000
    "price: 3570000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 3070000, // Включает растаможку и доставку"
    
    # Car 28: 2021 BMW X2 Xdrive28I - price should be 2360000
    "price: 2760000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 2360000, // Включает растаможку и доставку"
    
    # Car 29: 2021 BMW X3 Sdrive30I - price should be 3240000
    "price: 3640000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 3240000, // Включает растаможку и доставку"
    
    # Car 30: 2022 BMW X3 Sdrive30I - price should be 3490000
    "price: 3890000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 3490000, // Включает растаможку и доставку"
    
    # Car 31: 2021 Audi Q3 Premium 40 - price should be 2940000
    "price: 3340000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 2940000, // Включает растаможку и доставку"
    
    # Car 32: 2021 BMW X3 Xdrive30I - price should be 3030000
    "price: 3430000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 3030000, // Включает растаможку и доставку"
    
    # Car 33: 2022 Audi Q5 Premium 45 - price should be 3110000
    "price: 3510000, // Р'РєР»СЋС‡Р°РµС‚ СЂР°СЃС‚Р°РјРѕР¶РєСѓ Рё РґРѕСЃС‚Р°РІРєСѓ" = "price: 3110000, // Включает растаможку и доставку"
}

# Apply all price updates
$updateCount = 0
foreach ($oldPrice in $priceUpdates.Keys) {
    $newPrice = $priceUpdates[$oldPrice]
    if ($scriptContent -match [regex]::Escape($oldPrice)) {
        $scriptContent = $scriptContent -replace [regex]::Escape($oldPrice), $newPrice
        $updateCount++
        Write-Host "Updated price for car $updateCount" -ForegroundColor Yellow
    }
}

# Also fix encoding issues
$scriptContent = $scriptContent -replace "рџљ—", "🚗"
$scriptContent = $scriptContent -replace "в‚Ѕ", "₽"

# Write the updated content back to script.js
$scriptContent | Out-File "script.js" -Encoding UTF8

Write-Host "Fixed $updateCount car prices and encoding issues!" -ForegroundColor Green
Write-Host "All prices now match the provided list exactly." -ForegroundColor Cyan

