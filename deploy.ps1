# deploy.ps1 — 一鍵部署到 GitHub Pages + Cloudflare Pages
# 使用方式：在 PowerShell 執行 .\deploy.ps1
# （需要先安裝 Node.js，並已透過 wrangler login 登入 Cloudflare）

param(
    [string]$Message = ""
)

Set-Location $PSScriptRoot

# ── 1. 確認有未提交的變更 ──
$status = git status --porcelain
if ($status -or $Message) {
    $commitMsg = if ($Message) { $Message } else {
        "content: update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    }
    git add -A
    git commit -m $commitMsg
    if ($LASTEXITCODE -ne 0) { Write-Host "Nothing to commit." }
}

# ── 2. Push 到 GitHub（更新 GitHub Pages）──
Write-Host "`n▶ 推送到 GitHub..." -ForegroundColor Cyan
git push origin master
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ GitHub Pages 已更新：https://innovarad.github.io/military-blog/" -ForegroundColor Green
} else {
    Write-Host "⚠️  GitHub push 失敗，請檢查連線。" -ForegroundColor Yellow
}

# ── 3. 部署到 Cloudflare Pages ──
Write-Host "`n▶ 部署到 Cloudflare Pages..." -ForegroundColor Cyan
node -e "require('child_process').execSync('npx wrangler pages deploy . --project-name military-blog --branch master --commit-dirty=true', {stdio: 'inherit', shell: false})"
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Cloudflare Pages 已更新：https://military-blog.pages.dev/" -ForegroundColor Green
} else {
    Write-Host "⚠️  Cloudflare Pages 部署失敗。" -ForegroundColor Yellow
}

Write-Host "`n🎉 完成！" -ForegroundColor Green
