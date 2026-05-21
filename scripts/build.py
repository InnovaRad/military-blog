#!/usr/bin/env python3
"""
build.py — 前沿軍事觀察 自動建置腳本
======================================
功能：
  1. 掃描 articles/ 下所有子目錄，讀取 meta.json
  2. 使用 git log 取得各文章最後一次人工修改日期（排除 [skip ci] 提交）
  3. 更新各文章 index.html 內的 <span id="last-updated"> 日期
  4. 依日期（最新在前）重新生成 index.html 的卡片區塊

執行方式：
  python scripts/build.py        # 一般執行（需在 repo 根目錄）
  python scripts/build.py --dry  # 僅列印，不寫入檔案
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── 設定 ──────────────────────────────────────────────────
ROOT         = Path(__file__).resolve().parent.parent
ARTICLES_DIR = ROOT / 'articles'
ROOT_INDEX   = ROOT / 'index.html'
CARD_START   = '<!-- ARTICLES:START -->'
CARD_END     = '<!-- ARTICLES:END -->'
DRY_RUN      = '--dry' in sys.argv

# ── 日期工具 ──────────────────────────────────────────────

def git_last_human_date(filepath: Path) -> str:
    """
    回傳該檔案最後一次「人工提交」的日期（yyyy-mm-dd）。
    會排除包含 [skip ci] 的自動化提交。
    若 git log 失敗則回傳今日日期。
    """
    filepath_rel = filepath.relative_to(ROOT)

    def run_log(*extra_args):
        result = subprocess.run(
            ['git', 'log'] + list(extra_args) + ['-1', '--format=%ci', '--', str(filepath_rel)],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        return result.stdout.strip()

    # 優先：排除 [skip ci] 提交
    date_str = run_log('--invert-grep', '--grep=[skip ci]')
    if not date_str:
        # 回退：任何提交
        date_str = run_log()
    if not date_str:
        return datetime.now().strftime('%Y-%m-%d')

    try:
        # git 日期格式：2026-05-21 14:30:00 +0800
        dt = datetime.fromisoformat(date_str.rsplit(' ', 1)[0])
        return dt.strftime('%Y-%m-%d')
    except ValueError:
        return datetime.now().strftime('%Y-%m-%d')


def to_chinese_date(date_str: str) -> str:
    """'2026-05-21' → '2026年5月21日'"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return f'{dt.year}年{dt.month}月{dt.day}日'
    except ValueError:
        return date_str

# ── 文章掃描 ──────────────────────────────────────────────

def load_articles() -> list[dict]:
    articles = []
    for article_dir in sorted(ARTICLES_DIR.iterdir()):
        if not article_dir.is_dir():
            continue
        meta_file  = article_dir / 'meta.json'
        index_file = article_dir / 'index.html'
        if not meta_file.exists() or not index_file.exists():
            continue

        with open(meta_file, encoding='utf-8') as f:
            meta = json.load(f)

        slug = article_dir.name
        date = git_last_human_date(index_file)

        meta['slug']         = slug
        meta['date_updated'] = date
        meta['url']          = f'articles/{slug}/'

        # 更新文章頁面裡的日期
        update_article_date(index_file, date)

        articles.append(meta)
        print(f'  [article] {slug:30s}  {date}')

    # 最新在前
    articles.sort(key=lambda x: x.get('date_updated', '1970-01-01'), reverse=True)
    return articles

# ── 更新文章頁日期 ─────────────────────────────────────────

def update_article_date(index_file: Path, date_str: str) -> None:
    """將 <span id="last-updated">...</span> 更新為新日期"""
    with open(index_file, encoding='utf-8') as f:
        content = f.read()

    cn_date = to_chinese_date(date_str)
    pattern = r'(<span\s+id="last-updated"[^>]*>)([^<]*)(</span>)'
    new_content = re.sub(pattern, rf'\g<1>{cn_date}\g<3>', content)

    if new_content == content:
        return  # 無變更

    if not DRY_RUN:
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
    print(f'    → 日期已更新為 {cn_date}')

# ── 生成卡片 HTML ─────────────────────────────────────────

def make_card_html(article: dict) -> str:
    title    = article.get('title', '（未命名）')
    desc     = article.get('description', '')
    url      = article.get('url', '#')
    date_str = article.get('date_updated', '')
    tags     = article.get('tags', [])

    date_cn   = to_chinese_date(date_str)
    supabase_path = '/' + url  # e.g. /articles/modern-tank-warfare/

    tags_html = ''.join(
        f'              <span class="tag">{t}</span>\n'
        for t in tags[:4]
    )

    return f'''\
      <article class="card">
        <a href="{url}" class="card-link">
          <div class="card-body">
            <h2 class="card-title">{title}</h2>
            <p class="card-desc">{desc}</p>
            <div class="card-meta">
              <span class="card-date">{date_cn}</span>
              <span class="card-views" data-path="{supabase_path}">…</span>
            </div>
{('            <div class="card-tags">\n' + tags_html + '            </div>\n') if tags_html else ''}\
          </div>
        </a>
      </article>'''

# ── 更新根目錄 index.html ─────────────────────────────────

def update_root_index(articles: list[dict]) -> None:
    with open(ROOT_INDEX, encoding='utf-8') as f:
        content = f.read()

    cards = '\n'.join(make_card_html(a) for a in articles)
    block = f'{CARD_START}\n{cards}\n      {CARD_END}'

    pattern = re.escape(CARD_START) + r'.*?' + re.escape(CARD_END)
    new_content = re.sub(pattern, block, content, flags=re.DOTALL)

    if new_content == content:
        print('  [index]  無變更')
        return

    if not DRY_RUN:
        with open(ROOT_INDEX, 'w', encoding='utf-8') as f:
            f.write(new_content)
    print(f'  [index]  已更新（共 {len(articles)} 篇文章）')

# ── 主程式 ────────────────────────────────────────────────

def main() -> None:
    if DRY_RUN:
        print('[DRY RUN] 不會實際寫入檔案\n')

    print('掃描文章…')
    articles = load_articles()

    print(f'\n更新首頁（共 {len(articles)} 篇）…')
    update_root_index(articles)

    print('\n建置完成。')


if __name__ == '__main__':
    main()
