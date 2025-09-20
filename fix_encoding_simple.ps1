# Simple encoding fix
Write-Host "Fixing encoding in script.js..." -ForegroundColor Green

$content = Get-Content "script.js" -Raw -Encoding UTF8

# Fix the most common encoding issues
$content = $content -replace "Р'", "В"
$content = $content -replace "Рє", "к"
$content = $content -replace "Р»", "л"
$content = $content -replace "СЋ", "ю"
$content = $content -replace "С‡", "ч"
$content = $content -replace "Р°", "а"
$content = $content -replace "Рµ", "е"
$content = $content -replace "С‚", "т"
$content = $content -replace "СЂ", "р"
$content = $content -replace "СЃ", "с"
$content = $content -replace "Рј", "м"
$content = $content -replace "Рѕ", "о"
$content = $content -replace "Р¶", "ж"
$content = $content -replace "Сѓ", "у"
$content = $content -replace "Рё", "и"
$content = $content -replace "Рґ", "д"
$content = $content -replace "РІ", "в"
$content = $content -replace "РЅ", "н"
$content = $content -replace "Рі", "г"
$content = $content -replace "Р±", "б"
$content = $content -replace "Рџ", "П"
$content = $content -replace "Рњ", "М"
$content = $content -replace "Р"", "Д"
$content = $content -replace "Рћ", "О"
$content = $content -replace "РЎ", "С"
$content = $content -replace "Рљ", "К"
$content = $content -replace "Р–", "Ж"
$content = $content -replace "Рџ", "П"
$content = $content -replace "Р—", "З"
$content = $content -replace "Р¦", "Ц"
$content = $content -replace "Рљ", "К"
$content = $content -replace "Р¤", "Ф"
$content = $content -replace "Р™", "Й"
$content = $content -replace "Р›", "Л"
$content = $content -replace "РЄ", "Е"
$content = $content -replace "РЁ", "Ш"
$content = $content -replace "Р«", "Ы"
$content = $content -replace "РЎ", "С"
$content = $content -replace "Р§", "Ч"
$content = $content -replace "Рў", "Т"
$content = $content -replace "РЄ", "Е"
$content = $content -replace "РЁ", "Ш"
$content = $content -replace "Р«", "Ы"
$content = $content -replace "РЎ", "С"
$content = $content -replace "Р§", "Ч"
$content = $content -replace "Рў", "Т"

# Fix symbols
$content = $content -replace "рџљ—", "🚗"
$content = $content -replace "в‚Ѕ", "₽"

# Write back
$content | Out-File "script.js" -Encoding UTF8 -NoNewline

Write-Host "Encoding fixed!" -ForegroundColor Green

