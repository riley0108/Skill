---
name: supabase
description: 用 Supabase（開源 Firebase 替代品）蓋 app 的實作指南 —— Postgres + Auth + Row Level Security + Storage + Edge Functions + Realtime + CLI 本地開發。當使用者要「接 Supabase／寫 supabase-js 查詢／設定 Auth 登入（含 Next.js @supabase/ssr）／寫 RLS policy／用 Storage 上傳檔案／寫 Edge Function／訂閱 Realtime／用 supabase CLI 做 migration 與本地開發／產 TypeScript types」，或遇到「啟用 RLS 後查詢突然回空陣列、service_role 金鑰、connection pooling 連接埠、新版 publishable/secret 金鑰」等問題時使用。程式碼以 @supabase/supabase-js v2 + @supabase/ssr 為主，Python supabase-py 為輔。
---

# 🟢 Supabase 實作指南

Supabase = 託管 **PostgreSQL** + 自動 REST/GraphQL（PostgREST）+ Auth + Storage + Edge Functions（Deno）+ Realtime，全部用同一把 Postgres。心智模型：**你寫的是 Postgres，Supabase 把它變成 API**；安全靠 **Row Level Security（RLS）**，不是靠藏 API。

完整可複製貼上的程式碼與細節在 **[references/reference.md](references/reference.md)**（依下列 9 區編排）。本檔是導覽 + 最容易踩的雷。

## 🗺️ 該看哪一段（reference.md 內）
1. **Setup & Client** — 建 client、env 變數、server vs browser、🆕 publishable/secret 金鑰
2. **Database / 查詢** — select/insert/update/upsert/delete、filters、排序分頁、join、`.single()`、`.rpc()`、count
3. **Auth** — 註冊/登入/OAuth/OTP、`getUser` vs `getSession`、`@supabase/ssr`（Next.js）、`auth.uid()`
4. **RLS** — 啟用、policy（USING / WITH CHECK）、`auth.uid()`、常見 pattern
5. **Storage** — bucket（公開/私有）、上傳下載、`getPublicUrl`/`createSignedUrl`、storage RLS
6. **Edge Functions** — `Deno.serve`、`functions new/serve/deploy`、`functions.invoke()`、secrets
7. **Realtime** — `postgres_changes`、broadcast、presence、開 replication
8. **CLI & 本地開發** — `init/start/link`、migrations、`gen types`、seed
9. **Gotchas & 最佳實踐** — 含 connection pooling（Supavisor 5432 vs 6543）

## 🚀 30 秒起步
```bash
npm install @supabase/supabase-js
```
```javascript
import { createClient } from '@supabase/supabase-js'
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,  // 瀏覽器安全（受 RLS 保護）
)
const { data, error } = await supabase.from('todos').select('*').eq('done', false)
```
本地全套（需 Docker）：`supabase init && supabase start`（API:54321 / DB:54322 / Studio:54323）。

## ☠️ 最容易踩的 5 個雷（先記這個）
1. **啟用 RLS 後查詢回 `[]`／寫入被擋** = 還沒建 policy。RLS **預設全拒**，`ALTER TABLE ... ENABLE ROW LEVEL SECURITY` 後一定要配至少一條 `CREATE POLICY`。這是「查詢突然變空」第一大主因。
2. **`service_role` / `sb_secret_...` 金鑰永遠不可進前端** —— 它**繞過 RLS**，只能放後端／Edge Function。前端只用 `anon` / `sb_publishable_...`。
3. **`public` schema 的表一律要開 RLS** —— 它透過 PostgREST 對外可達，沒開 RLS = anon 能讀寫全部。
4. **伺服器端授權用 `getUser()`／`getClaims()`，不要用 `getSession()`** —— session 來自儲存、未重新驗證，可被偽造。`@supabase/ssr` 的 cookie 要用 `getAll`/`setAll`（別用已淘汰的 `get`/`set`/`remove`，會壞掉 session 刷新）。
5. **policy 裡用 `(select auth.uid())` 包起來**（每語句快取一次），別裸寫 `auth.uid() = user_id`（每列算一次，大表慢 90%+）。授權看 `app_metadata`（使用者改不了），**絕不**看 `user_metadata`（使用者可改）。

## 🔑 2026 金鑰新制（容易搞混，務必知道）
- 新制 **publishable（`sb_publishable_...`，取代 `anon`）** + **secret（`sb_secret_...`，取代 `service_role`）**，是不透明可獨立輪替的 token。
- 2025-11-01 起新專案預設只給新金鑰；舊 `anon`/`service_role` 預計 2026 底移除。新舊可並存，逐一替換。
- 新金鑰走 **`apikey` header**（不是 `Authorization: Bearer`，它不是 JWT）。
- 但 Postgres **角色**名稱不變：仍是 `anon` / `authenticated` / `service_role`。

## 🐍 Python（supabase-py）
方法是 snake_case 且**要 `.execute()`**：`supabase.table('todos').select('*').eq('done', False).execute()`。詳見 reference.md。

> 來源：Supabase 官方文件（supabase.com/docs），核對於 2026-06。API 演進快 —— 金鑰命名、`@supabase/ssr` cookie API、Edge Functions `Deno.serve`、Supavisor pooling 都是近期變動，動到時以官方文件再確認一次。
