# Final encoding fix
Write-Host "Final encoding fix..." -ForegroundColor Green

$content = Get-Content "script.js" -Raw -Encoding UTF8

# Replace all problematic characters
$replacements = @{
    "Р'" = "В"
    "Рє" = "к" 
    "Р»" = "л"
    "СЋ" = "ю"
    "С‡" = "ч"
    "Р°" = "а"
    "Рµ" = "е"
    "С‚" = "т"
    "СЂ" = "р"
    "СЃ" = "с"
    "Рј" = "м"
    "Рѕ" = "о"
    "Р¶" = "ж"
    "Сѓ" = "у"
    "Рё" = "и"
    "Рґ" = "д"
    "РІ" = "в"
    "РЅ" = "н"
    "Рі" = "г"
    "Р±" = "б"
    "Рџ" = "П"
    "Рњ" = "М"
    "Р"" = "Д"
    "Рћ" = "О"
    "РЎ" = "С"
    "Рљ" = "К"
    "Р–" = "Ж"
    "Р—" = "З"
    "Р¦" = "Ц"
    "Р¤" = "Ф"
    "Р™" = "Й"
    "Р›" = "Л"
    "РЄ" = "Е"
    "РЁ" = "Ш"
    "Р«" = "Ы"
    "Р§" = "Ч"
    "Рў" = "Т"
    "рџљ—" = "🚗"
    "в‚Ѕ" = "₽"
}

foreach ($old in $replacements.Keys) {
    $new = $replacements[$old]
    $content = $content -replace [regex]::Escape($old), $new
}

# Write back with UTF-8 encoding
[System.IO.File]::WriteAllText("script.js", $content, [System.Text.Encoding]::UTF8)

Write-Host "Encoding fixed!" -ForegroundColor Green

