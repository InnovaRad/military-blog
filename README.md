# 前沿軍事觀察 — 部落格架設指南

## 專案結構

```
/
├── index.html                       # 首頁（由 build.py 自動維護）
├── css/style.css                    # 全站樣式
├── js/
│   ├── config.js                    # Supabase 設定（需填入您的金鑰）
│   └── counter.js                   # 瀏覽計數器
├── articles/
│   └── modern-tank-warfare/
│       ├── index.html               # 文章頁面
│       └── meta.json                # 文章 metadata
├── scripts/build.py                 # 建置腳本
├── .github/workflows/deploy.yml     # CI/CD 自動部署
└── supabase-setup.sql               # Supabase 資料庫初始化
```

---

## 一、初始化 Supabase 計數器

1. 前往 [https://app.supabase.com](https://app.supabase.com) 建立一個新專案。
2. 進入 **SQL Editor**，貼上 `supabase-setup.sql` 全文並執行。
3. 進入 **Settings → API**，複製：
   - **Project URL**（格式：`https://xxxx.supabase.co`）
   - **anon public** 金鑰
4. 編輯 `js/config.js`，填入上述兩個值。

---

## 二、推送到 GitHub Pages

```bash
git init
git add .
git commit -m "init: military blog"
git remote add origin https://github.com/<你的帳號>/<repo名>.git
git push -u origin main
```

**啟用 GitHub Pages**：
- 進入 GitHub repo → **Settings → Pages**
- Source 選 **Deploy from a branch**，Branch 選 **`gh-pages`**，目錄選 `/（root）`

第一次 push 後，GitHub Actions 會自動建置並部署至 `gh-pages` 分支。

---

## 三、串接 Cloudflare Pages

1. 前往 [https://dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages → Create application → Pages**。
2. 選 **「直接上傳」** 或連接 GitHub repo（選 **gh-pages** 分支，無需建置命令）。
   - **Framework preset**：None
   - **Build command**：（空白）
   - **Build output directory**：`/`
3. 記下 **Cloudflare Pages 網址**（格式：`https://<project>.pages.dev`）。

**設定 GitHub Secrets**（讓 CI 能直接推送）：
進入 GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**，新增：

| Secret 名稱 | 取得位置 |
|---|---|
| `CLOUDFLARE_API_TOKEN` | Cloudflare Dashboard → My Profile → API Tokens（需有 Pages 編輯權限） |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Dashboard 首頁右下角 |
| `CLOUDFLARE_PROJECT_NAME` | 步驟 2 建立的 Pages 專案名稱 |

設定完成後，每次 `git push` 到 `main`，GitHub Actions 會同時更新 GitHub Pages 與 Cloudflare Pages。

---

## 四、新增文章

1. 在 `articles/` 下建立新目錄，例如 `articles/f35-overview/`。
2. 在目錄內建立兩個檔案：

**`meta.json`**（修改內容）：
```json
{
  "slug": "f35-overview",
  "title": "F-35 閃電 II：匿蹤航空的新世代",
  "author": "李建宏",
  "author_title": "航空工程師",
  "description": "深入分析 F-35 三種型號的差異……",
  "tags": ["航空", "匿蹤", "F-35", "美國空軍"]
}
```

**`index.html`**：複製 `articles/modern-tank-warfare/index.html`，替換：
- `<title>` 標題
- `<meta name="description">` 描述
- 題圖 `<img src="...">` 與 `alt`
- `<span id="last-updated">` 日期（build.py 會自動更新）
- `.view-count` 的 `data-path`（改為 `/articles/f35-overview/`）
- footer 圖片出處說明
- 文章正文

3. `git add . && git commit -m "article: 新增 F-35 概覽" && git push`

CI 自動執行：首頁卡片新增、日期更新、部署。

---

## 五、本機開發

```bash
# 更新日期、重建首頁（需有 git 歷史）
python scripts/build.py

# 預覽（任一靜態伺服器均可）
python -m http.server 8080
# 開啟 http://localhost:8080
```

---

## 六、圖片出處標示規範（CC BY）

本站題圖依創用 CC 授權標示，footer 中必須包含：

- **作品名稱**（連結至原始頁面）
- **作者姓名**
- **來源平台**（如 Wikimedia Commons）
- **授權條款名稱與連結**（如 CC BY-SA 3.0）
