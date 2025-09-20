# Script to update car prices in script.js
Write-Host "Updating car prices in script.js..." -ForegroundColor Green

# Read the current script.js file
$scriptContent = Get-Content "script.js" -Raw

# Define price updates (old price -> new price)
$priceUpdates = @{
    "price: 1790000" = "price: 1490000"  # Car 7
    "price: 1720000" = "price: 1420000"  # Car 8
    "price: 1620000" = "price: 1320000"  # Car 9
    "price: 1560000" = "price: 1260000"  # Car 10
    "price: 2410000" = "price: 2110000"  # Car 11
    "price: 2310000" = "price: 2010000"  # Car 12
    "price: 2330000" = "price: 2030000"  # Car 13
    "price: 2070000" = "price: 1770000"  # Car 14
    "price: 2180000" = "price: 1880000"  # Car 15
    "price: 3450000" = "price: 3150000"  # Car 16
    "price: 2260000" = "price: 1960000"  # Car 17
    "price: 1690000" = "price: 1390000"  # Car 18
    "price: 2030000" = "price: 1730000"  # Car 19
    "price: 1780000" = "price: 1480000"  # Car 20
    "price: 2210000" = "price: 1910000"  # Car 21
    "price: 2820000" = "price: 2520000"  # Car 22
    "price: 1890000" = "price: 1590000"  # Car 23
    "price: 2050000" = "price: 1750000"  # Car 24
    "price: 2000000" = "price: 1700000"  # Car 25
    "price: 1980000" = "price: 1680000"  # Car 26
    "price: 3370000" = "price: 3070000"  # Car 27
    "price: 2660000" = "price: 2360000"  # Car 28
    "price: 3540000" = "price: 3240000"  # Car 29
    "price: 3790000" = "price: 3490000"  # Car 30
    "price: 3240000" = "price: 2940000"  # Car 31
    "price: 3330000" = "price: 3030000"  # Car 32
    "price: 3410000" = "price: 3110000"  # Car 33
}

# Apply price updates
foreach ($oldPrice in $priceUpdates.Keys) {
    $newPrice = $priceUpdates[$oldPrice]
    $scriptContent = $scriptContent -replace [regex]::Escape($oldPrice), $newPrice
    Write-Host "Updated: $oldPrice -> $newPrice" -ForegroundColor Yellow
}

# Write the updated content back to script.js
$scriptContent | Out-File "script.js" -Encoding UTF8

Write-Host "All car prices updated successfully!" -ForegroundColor Green
Write-Host "Prices now include customs and delivery costs as specified." -ForegroundColor Cyan

