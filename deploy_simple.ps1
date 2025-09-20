param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubUsername
)

$repoName = "carshop-website"
$remoteUrl = "https://github.com/$GitHubUsername/$repoName.git"

Write-Host "=== GitHub Deployment Script ==="

# Check if Git is installed
try {
    git --version | Out-Null
    Write-Host "Git is installed." -ForegroundColor Green
} catch {
    Write-Host "Error: Git is not installed. Please install Git from https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

# Initialize Git repository
if (-not (Test-Path .git)) {
    Write-Host "Initializing Git repository..."
    git init
    Write-Host "Git repository initialized." -ForegroundColor Green
} else {
    Write-Host "Git repository already initialized." -ForegroundColor Yellow
}

# Add all files
Write-Host "Adding all files to staging..."
git add .
Write-Host "All files added." -ForegroundColor Green

# Commit changes
Write-Host "Committing changes..."
git commit -m "Initial commit: CarExport website deployment"
Write-Host "Changes committed." -ForegroundColor Green

# Set remote origin
Write-Host "Setting remote origin to $remoteUrl..."
try {
    git remote add origin $remoteUrl
    Write-Host "Remote origin added." -ForegroundColor Green
} catch {
    Write-Host "Remote origin already exists or error adding. Attempting to set URL..." -ForegroundColor Yellow
    git remote set-url origin $remoteUrl
    Write-Host "Remote origin URL set." -ForegroundColor Green
}

# Push to GitHub
Write-Host "Pushing to GitHub (main branch)..."
try {
    git push -u origin main
    Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Your site should be available at https://$GitHubUsername.github.io/$repoName after configuring GitHub Pages." -ForegroundColor Cyan
} catch {
    Write-Host "Error pushing to GitHub. Please check your credentials and repository settings." -ForegroundColor Red
    Write-Host "You might need to generate a Personal Access Token (PAT) if you're using 2FA." -ForegroundColor Yellow
    Write-Host "Instructions: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token" -ForegroundColor Yellow
    exit 1
}

Write-Host "Deployment script finished."

