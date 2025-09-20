# Generates car-info.json manifests for each images/car* directory (JPG only)
$ErrorActionPreference = 'Stop'

$root = "images"
$exts = @('.jpg', '.JPG')

function Add-ByRegex {
    param(
        [array]$files,
        [regex]$regex,
        [ref]$ordered
    )
    $matches = $files | Where-Object { $_.BaseName -match $regex } |
        Sort-Object { [int]([regex]::Match($_.BaseName, $regex).Groups[1].Value) }
    foreach ($f in $matches) {
        if ($ordered.Value -notcontains $f.Name) { $ordered.Value += $f.Name }
    }
}

$dirs = Get-ChildItem -Path $root -Directory -Filter 'car*'
foreach ($d in $dirs) {
    $files = Get-ChildItem -Path $d.FullName -File |
        Where-Object { $exts -contains $_.Extension }

    $ordered = @()

    # main.* (если есть) – первой
    $mainFile = Get-ChildItem -Path $d.FullName -File -Filter 'main.*' |
        Where-Object { $exts -contains $_.Extension } | Select-Object -First 1
    if ($mainFile) { $ordered += $mainFile.Name }

    # original1..original30, original (1..30), 1 (1..30), photo1..photo30, 1..30
    Add-ByRegex -files $files -regex 'original(\d+)$' -ordered ([ref]$ordered)
    Add-ByRegex -files $files -regex '^original \((\d+)\)$' -ordered ([ref]$ordered)
    Add-ByRegex -files $files -regex '^1 \((\d+)\)$' -ordered ([ref]$ordered)
    Add-ByRegex -files $files -regex 'photo(\d+)$' -ordered ([ref]$ordered)
    Add-ByRegex -files $files -regex '^(\d+)$' -ordered ([ref]$ordered)

    # Именованные частые варианты
    $named = @('front','face','exterior','left','right','rear','back','interior','dashboard','engine')
    foreach ($n in $named) {
        $namedFiles = $files | Where-Object { $_.BaseName -ieq $n }
        foreach ($f in $namedFiles) { if ($ordered -notcontains $f.Name) { $ordered += $f.Name } }
    }

    # Остальные по алфавиту
    $remaining = $files | Where-Object { $ordered -notcontains $_.Name } | Sort-Object Name
    $ordered += ($remaining | ForEach-Object { $_.Name })

    $manifest = @{ photos = $ordered }
    $json = $manifest | ConvertTo-Json -Depth 3
    $outPath = Join-Path $d.FullName 'car-info.json'
    [System.IO.File]::WriteAllText($outPath, $json, [System.Text.Encoding]::UTF8)
    Write-Host "Wrote manifest:" $outPath
}
