-- =============================================================
-- Supabase 瀏覽計數器設定
-- 請在 Supabase Dashboard → SQL Editor 貼上並執行此腳本
-- =============================================================

-- 1. 建立 page_views 資料表
CREATE TABLE IF NOT EXISTS public.page_views (
  id         UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
  path       TEXT        NOT NULL UNIQUE,
  views      BIGINT      NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 2. 啟用 Row Level Security
ALTER TABLE public.page_views ENABLE ROW LEVEL SECURITY;

-- 3. 允許任何人讀取（公開計數）
CREATE POLICY "public_read" ON public.page_views
  FOR SELECT USING (true);

-- 4. 建立原子遞增函式（安全執行者，繞過 RLS）
CREATE OR REPLACE FUNCTION public.increment_page_view(page_path TEXT)
RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  new_views BIGINT;
BEGIN
  INSERT INTO public.page_views (path, views)
  VALUES (page_path, 1)
  ON CONFLICT (path) DO UPDATE
    SET views      = page_views.views + 1,
        updated_at = now()
  RETURNING views INTO new_views;

  RETURN new_views;
END;
$$;

-- 5. 授予 anon 角色執行函式的權限
GRANT EXECUTE ON FUNCTION public.increment_page_view(TEXT) TO anon;

-- （選用）預先插入首頁與第一篇文章的計數列
INSERT INTO public.page_views (path, views)
VALUES
  ('/', 0),
  ('/articles/modern-tank-warfare/', 0)
ON CONFLICT (path) DO NOTHING;
