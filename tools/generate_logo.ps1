param(
    [Parameter(Mandatory=$true)]
    [string]$SourceImagePath,

    [string]$OutDir = "images"
)

$ErrorActionPreference = "Stop"

function Ensure-Dir($path){ if(-not (Test-Path $path)){ New-Item -ItemType Directory -Force -Path $path | Out-Null } }

Ensure-Dir $OutDir

Add-Type -AssemblyName System.Drawing

function New-SquareImage {
    param(
        [System.Drawing.Image]$Image,
        [int]$Size,
        [string]$OutFile
    )

    $bmp = New-Object System.Drawing.Bitmap $Size, $Size, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
    $gfx = [System.Drawing.Graphics]::FromImage($bmp)
    $gfx.SmoothingMode = 'HighQuality'
    $gfx.InterpolationMode = 'HighQualityBicubic'
    $gfx.PixelOffsetMode = 'HighQuality'

    # Fill with transparent background to look good on dark theme
    $gfx.Clear([System.Drawing.Color]::FromArgb(0,0,0,0))

    $ratioX = $Size / $Image.Width
    $ratioY = $Size / $Image.Height
    $ratio = [Math]::Min($ratioX, $ratioY)
    $newWidth = [int]([Math]::Round($Image.Width * $ratio))
    $newHeight = [int]([Math]::Round($Image.Height * $ratio))

    $posX = [int](($Size - $newWidth) / 2)
    $posY = [int](($Size - $newHeight) / 2)

    $destRect = New-Object System.Drawing.Rectangle $posX, $posY, $newWidth, $newHeight
    $gfx.DrawImage($Image, $destRect)
    $gfx.Dispose()

    $bmp.Save($OutFile, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
}

if(-not (Test-Path $SourceImagePath)){ throw "File not found: $SourceImagePath" }
$img = [System.Drawing.Image]::FromFile($SourceImagePath)

# Primary logo and common favicon sizes
New-SquareImage -Image $img -Size 512 -OutFile (Join-Path $OutDir 'logo.png')
New-SquareImage -Image $img -Size 180 -OutFile (Join-Path $OutDir 'apple-touch-icon.png')
New-SquareImage -Image $img -Size 192 -OutFile (Join-Path $OutDir 'android-chrome-192x192.png')
New-SquareImage -Image $img -Size 512 -OutFile (Join-Path $OutDir 'android-chrome-512x512.png')
New-SquareImage -Image $img -Size 32  -OutFile (Join-Path $OutDir 'favicon-32x32.png')
New-SquareImage -Image $img -Size 16  -OutFile (Join-Path $OutDir 'favicon-16x16.png')

$img.Dispose()

Write-Host "✅ Generated icons in '$OutDir'." -ForegroundColor Green
Write-Host "Add these tags to your <head> if not present:" -ForegroundColor Yellow
@(
    '<link rel="apple-touch-icon" sizes="180x180" href="images/apple-touch-icon.png">',
    '<link rel="icon" type="image/png" sizes="32x32" href="images/favicon-32x32.png">',
    '<link rel="icon" type="image/png" sizes="16x16" href="images/favicon-16x16.png">',
    '<link rel="manifest" href="site.webmanifest">'
) | ForEach-Object { Write-Host "  $_" }


