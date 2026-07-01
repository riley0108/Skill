# Supabase Reference (2026)

> 程式碼以 `@supabase/supabase-js` **v2** + `@supabase/ssr` 為主，Python `supabase-py` 標註於相關處。核對於 supabase.com/docs，2026-06。

---

## 1. Project Setup & Client Init

### Install & basic client

```bash
npm install @supabase/supabase-js
```

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'https://xyzcompany.supabase.co', // project URL
  'sb_publishable_...'              // publishable key (或舊版 anon key)
)
```

Common options:

```javascript
const supabase = createClient(url, key, {
  db: { schema: 'public' },
  auth: { autoRefreshToken: true, persistSession: true, detectSessionInUrl: true },
  global: { headers: { 'x-my-custom-header': 'my-app-name' } },
})
```

### Env var conventions

```bash
# .env.local (Next.js)
NEXT_PUBLIC_SUPABASE_URL=https://xyzcompany.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...   # 可安全送到瀏覽器
SUPABASE_SECRET_KEY=sb_secret_...                         # server-only，絕不加 NEXT_PUBLIC
```

- **Next.js**: `NEXT_PUBLIC_*` · **Vite**: `VITE_*`（`import.meta.env.VITE_...`）· **Expo**: `EXPO_PUBLIC_*` · **CRA (legacy)**: `REACT_APP_*`
- 仍會看到的舊命名：`NEXT_PUBLIC_SUPABASE_ANON_KEY`、`SUPABASE_SERVICE_ROLE_KEY`。

### Server vs browser client

- **Browser client** 把 session 存在 storage、自動刷新 token。
- **Server client** 透過 request cookie 讀寫 session，每個 request 以登入者身分認證。RLS 仍生效。
- 後端要繞過 RLS 的特權操作：用 **secret key** 另建一個 client，且絕不暴露給瀏覽器。

### ⚠️ 近期變動 — 新 publishable/secret 金鑰 vs 舊 anon/service_role

Supabase 用**不透明隨機 token** 取代舊的 JWT-based 金鑰，可獨立輪替、即時撤銷，secret key 還會被擋下瀏覽器使用。

| 新金鑰 | 取代 | 前綴 | 權限 | 用在哪 |
|---|---|---|---|---|
| **Publishable** | `anon` | `sb_publishable_...` | 低（受 RLS） | 瀏覽器、行動端、公開 repo |
| **Secret** | `service_role` | `sb_secret_...` | 高（繞過 RLS） | 後端、Edge Functions —— 絕不進前端 |

**時程**：2025-06 early access；2025-07 全面開放。**2025-11-01 起新專案預設不再發 `anon`/`service_role`**；舊金鑰預計 **2026 底移除**。遷移非破壞性 —— 新舊並存，逐一替換 client。

**使用注意**：
- 新金鑰只放 **`apikey` header** —— 它不是 JWT，用 `Authorization: Bearer` 會解析失敗（除非 Bearer 值剛好等於 apikey）。
- Edge Functions 用新金鑰需 `--no-verify-jwt`（自己在函式內做授權）。
- 新 env 變數 `SUPABASE_PUBLISHABLE_KEY` / `SUPABASE_SECRET_KEY` 與舊 `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY` 並存。
- 同期還有 **JWT signing keys** 改用非對稱（ES256/RS256），可本地驗 JWT（`getClaims()`）。

> 注意：變的是 *API key* 名稱，Postgres **角色**仍是 `anon` / `authenticated` / `service_role`。

### Python client (`supabase-py`)

```bash
pip install supabase
```

```python
import os
from supabase import create_client, Client

supabase: Client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
# Async: supabase = await acreate_client(url, key)
```

> Python 方法是 snake_case（`.maybe_single()`），且**一定要 `.execute()`** 才會跑。

---

## 2. Database / PostgREST Queries

每個查詢回 `{ data, error }`（視情況含 `count`/`status`）。JS 在 `await` 時執行；Python 要 `.execute()`。

```javascript
// SELECT
await supabase.from('characters').select()           // 全部欄位
await supabase.from('characters').select('id, name') // 指定欄位

// INSERT（預設不回傳 row，除非鏈 .select()）
await supabase.from('countries').insert({ id: 1, name: 'Mordor' })
await supabase.from('countries').insert([{ id: 1, name: 'Mordor' }, { id: 2, name: 'The Shire' }])
await supabase.from('countries').insert({ id: 1, name: 'Mordor' }).select()

// UPDATE（必須有 filter）
await supabase.from('instruments').update({ name: 'piano' }).eq('id', 1).select()

// UPSERT
await supabase.from('instruments').upsert({ id: 1, name: 'piano' }).select()
await supabase.from('users').upsert({ username: 'supabot' }, { onConflict: 'username' })
await supabase.from('users').upsert({ username: 'supabot' }, { onConflict: 'username', ignoreDuplicates: true })

// DELETE（必須有 filter，否則什麼都不刪）
await supabase.from('countries').delete().eq('id', 1)
await supabase.from('countries').delete().in('id', [1, 2, 3])
await supabase.from('countries').delete().eq('id', 1).select() // 回傳被刪的 row
```

### Filters

```javascript
.eq('name', 'violin')            .neq('name', 'viola')
.gt('age', 5)    .gte('age', 5)  .lt('age', 5)    .lte('age', 5)
.like('name', '%lin')            .ilike('name', '%LIN')
.is('ended_at', null)            .in('name', ['violin', 'harp'])
.contains('tags', ['a'])         .containedBy('tags', ['a','b'])
.overlaps('tags', ['a','b'])     .textSearch('body', "'cat' & 'dog'", { type: 'websearch', config: 'english' })

// 否定
.not('name', 'is', null)

// OR（PostgREST 逗號字串）
.or('id.eq.2,name.eq.Han')
.or('and(name.eq.Han,id.eq.2),id.eq.3')
.or('name.eq.flute,name.eq.guitar', { referencedTable: 'instruments' })

// AND = 鏈 filter
.eq('status', 'active').gte('age', 18)

// 原始 / 簡寫
.filter('name', 'in', '("Han","Luke")')
.match({ id: 2, name: 'Han' })
```

### Ordering & pagination

```javascript
.order('id', { ascending: false })
.order('name', { ascending: true, nullsFirst: false })
.order('name', { referencedTable: 'instruments', ascending: true })

.limit(10)
.range(0, 9)   // 兩端皆含、0-indexed = 前 10 列
.limit(10, { referencedTable: 'instruments' })
```

### Embedded resources / joins

```javascript
// 一對多（FK 自動偵測）
.select(`name, instruments ( name )`)

// 多對多（透過 junction table）
.select(`name, teams ( name )`)

// 同表兩個 FK — 消歧 + alias
.select(`content, from:sender_id ( name ), to:receiver_id ( name )`)

// inner join（只回有 match 的列）
.select('name, instruments!inner(name)')

// 過濾 embedded 欄位
.select('name, instruments(name)').eq('instruments.name', 'guitar')
```

### `.single()` / `.maybeSingle()`

```javascript
// .single() — 剛好一列；0 或 >1 => error；回物件不是陣列
await supabase.from('characters').select('name').eq('id', 1).single()

// .maybeSingle() — 0 或 1 列；0 => data 為 null（不報錯）；>1 => error
await supabase.from('characters').select('name').eq('id', 1).maybeSingle()
```

### `.rpc()` — 呼叫 Postgres function

```javascript
await supabase.rpc('hello_world')
await supabase.rpc('echo', { say: '👋' })
await supabase.rpc('list_stored_countries').eq('id', 1).single() // 回 setof 可鏈 filter
await supabase.rpc('hello_world', undefined, { get: true })       // 唯讀以 cacheable GET 呼叫
```

```sql
create or replace function echo(say text) returns text language sql as $$ select say; $$;
```

### Count & head

```javascript
const { count } = await supabase.from('characters').select('*', { count: 'exact', head: true })
const { data, count } = await supabase.from('characters').select('*', { count: 'exact' })
```

`count`：`'exact'`（精確、慢）、`'planned'`（planner 估計、快）、`'estimated'`（小表精確、大表估計）。`head: true` 只回 header。Mutation 預設不回 row —— 要鏈 `.select()`。

---

## 3. Auth

```javascript
// 註冊
await supabase.auth.signUp({ email, password, options: { data: { first_name: 'John' }, emailRedirectTo: 'https://example.com/welcome' } })
await supabase.auth.signUp({ phone: '+13334445555', password, options: { channel: 'sms' } })

// 密碼登入（錯誤不透露是帳號還是密碼錯 —— 防列舉）
await supabase.auth.signInWithPassword({ email, password })

// OAuth
await supabase.auth.signInWithOAuth({ provider: 'github', options: { redirectTo: '...', scopes: 'repo gist' } })

// Magic link / OTP — 是連結還是驗證碼由 email 樣板決定
// ({{ .ConfirmationURL }} = 連結, {{ .Token }} = 驗證碼)
await supabase.auth.signInWithOtp({ email, options: { shouldCreateUser: true } })
await supabase.auth.signInWithOtp({ phone: '+13334445555' })

// 驗證 OTP / token hash
await supabase.auth.verifyOtp({ email, token, type: 'email' })
await supabase.auth.verifyOtp({ phone, token, type: 'sms' })
await supabase.auth.verifyOtp({ token_hash, type: 'email' })
```

### getUser vs getSession（安全關鍵）

```javascript
const { data: { user } }    = await supabase.auth.getUser()    // 向 Auth server 重新驗證 JWT
const { data: { session } } = await supabase.auth.getSession() // 讀 storage，不重新驗證
```

- `getSession()` 在 server 端可被竄改/偽造（沒重新驗證）—— 伺服器授權**絕不**靠它。
- `getUser()` 一律向 Auth server 重新驗證 —— 可安全用於授權。
- **現代做法**：`getClaims()` 用已發佈的 public key 在本地驗 JWT（不用 round trip）。Server 端授權用 `getClaims()`/`getUser()`，不要用 `getSession()`。

### signOut & listener

```javascript
await supabase.auth.signOut()                  // global（預設）— 全裝置
await supabase.auth.signOut({ scope: 'local' }) // 只當前 session

const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => { /* ... */ })
subscription.unsubscribe()
// 事件：INITIAL_SESSION, SIGNED_IN, SIGNED_OUT, TOKEN_REFRESHED, USER_UPDATED, PASSWORD_RECOVERY
```

> 別在 callback 裡 `await` 其他 Supabase 呼叫 —— 可能死鎖。重活用 `setTimeout(..., 0)` 延後。

### `@supabase/ssr` for Next.js (App Router)

```bash
npm install @supabase/supabase-js @supabase/ssr
```

> cookie 設定只用 **`getAll`** 與 **`setAll`**。已淘汰的逐項 `get`/`set`/`remove` 會壞掉 session 刷新。

```typescript
// lib/supabase/client.ts — Browser
import { createBrowserClient } from '@supabase/ssr'
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
  )
}
```

```typescript
// lib/supabase/server.ts — Server
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies() // Next 15+: async
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() { return cookieStore.getAll() },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) => cookieStore.set(name, value, options))
          } catch { /* Server Component — 若 middleware 會刷新 session 可忽略 */ }
        },
      },
    }
  )
}
```

```typescript
// middleware.ts — 每個 request 刷新 auth token
import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request })
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() { return request.cookies.getAll() },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) => supabaseResponse.cookies.set(name, value, options))
        },
      },
    }
  )
  await supabase.auth.getUser() // 重要：重新驗證 + 刷新。不要用 getSession()
  return supabaseResponse
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)'],
}
```

> Server Component 不能寫 cookie —— middleware 負責刷新 token、寫回輪替後的 cookie。建立新的 `NextResponse`（例如 redirect）時要把 Supabase cookie 帶過去，否則 session 會無聲掉。

### `auth.uid()` in SQL

```sql
select auth.uid();  -- 當前使用者 UUID，未登入為 NULL（讀 JWT 'sub' claim）

create table profiles (
  id uuid primary key references auth.users (id) default auth.uid(),
  display_name text
);
```

---

## 4. Row Level Security (RLS)

RLS 是 PostgreSQL 在**列層級**過濾存取 —— 等於替每個查詢自動加上你 policy 的 `WHERE`。Supabase 用 publishable key 把 `public` schema 暴露給瀏覽器，靠 RLS 才安全。

```sql
alter table public.profiles enable row level security;

grant select on public.profiles to anon;
grant select, insert, update, delete on public.profiles to authenticated;
```

### ⚠️ 關鍵雷

> 一旦 `ENABLE ROW LEVEL SECURITY`，這張表透過 API **完全不可存取**（讀回 0 列、寫入被擋），**直到你加至少一條 policy**。RLS 預設全拒。這是「我的查詢突然回 `[]`」第一大主因。啟用 RLS 一定要同時建 policy。

### Policy 語法 + USING vs WITH CHECK

```sql
create policy "policy_name"
on table_name
for { select | insert | update | delete | all }
to { anon | authenticated }
using ( <讀取/可見條件> )       -- SELECT/UPDATE/DELETE
with check ( <寫入驗證條件> );  -- INSERT/UPDATE
```

| 子句 | 意義 | 適用 |
|---|---|---|
| **`USING`** | 操作能看到/鎖定哪些既有列 | SELECT, UPDATE, DELETE |
| **`WITH CHECK`** | 寫入後新/改的列必須滿足的條件 | INSERT, UPDATE |

- INSERT 只用 `WITH CHECK`；DELETE 只用 `USING`；UPDATE 兩者都要。UPDATE 一列通常還需要 SELECT policy 讓它可見。

### Helpers + 效能

```sql
auth.uid()  -- 請求者 UUID（未登入為 NULL）
auth.jwt()  -- 完整解碼的 JWT（jsonb）
```

> 授權看 `app_metadata`（使用者**改不了**）。**絕不**看 `user_metadata`（使用者可改）。

⚡ 把 auth function 包進 scalar 子查詢，Postgres 就**每語句算一次**（快取），不是每列算：

```sql
using ( auth.uid() = user_id );          -- 慢（每列）
using ( (select auth.uid()) = user_id ); -- 快（大表快 94–99%）
```

另外：policy 比對的欄位要**建索引**、指定 `TO` 角色、client 查詢同步帶上同樣 filter。

### 常見 pattern

```sql
-- 使用者擁有該列
create policy "read own"   on profiles for select to authenticated using ( (select auth.uid()) = user_id );
create policy "insert own" on profiles for insert to authenticated with check ( (select auth.uid()) = user_id );
create policy "update own" on profiles for update to authenticated
  using ( (select auth.uid()) = user_id ) with check ( (select auth.uid()) = user_id );
create policy "delete own" on profiles for delete to authenticated using ( (select auth.uid()) = user_id );

-- 公開讀
create policy "public read" on posts for select to anon, authenticated using ( true );

-- 僅登入者
create policy "auth only" on documents for select to authenticated using ( true );
```

### Roles

| 角色 | 何時 | RLS |
|---|---|---|
| `anon` | 無/無效 JWT（publishable key、無 session） | 生效 |
| `authenticated` | 有效使用者 JWT | 生效 |
| `service_role` | 後端 admin（secret key） | **完全繞過 RLS** |

---

## 5. Storage

### Buckets

| | Private（預設） | Public |
|---|---|---|
| 讀 | RLS + JWT，或 signed URL | 任何人有 URL 即可（CDN） |
| 寫/刪/移 | 一律受 RLS | 一律受 RLS |

```javascript
await supabase.storage.createBucket('avatars', {
  public: true,
  allowedMimeTypes: ['image/*'],
  fileSizeLimit: '1MB',
})
await supabase.storage.getBucket('avatars')
await supabase.storage.listBuckets()
await supabase.storage.updateBucket('avatars', { public: false })
await supabase.storage.emptyBucket('avatars')
await supabase.storage.deleteBucket('avatars') // 必須先清空
```

### Object operations

```javascript
const bucket = supabase.storage.from('avatars')

await bucket.upload('public/avatar1.png', file, { cacheControl: '3600', contentType: 'image/png', upsert: false })
await bucket.update('public/avatar1.png', newFile, { upsert: true })
const { data: blob } = await bucket.download('public/avatar1.png', { download: 'my-name.png' })
await bucket.list('public', { limit: 100, offset: 0, sortBy: { column: 'name', order: 'asc' }, search: 'avatar' })
await bucket.remove(['public/avatar1.png', 'public/avatar2.png'])
await bucket.move('public/a.png', 'public/a-old.png')
await bucket.copy('public/a.png', 'public/a-copy.png')
```

### URLs

```javascript
// Public bucket — 同步、不驗證是否存在
const { data } = supabase.storage.from('avatars').getPublicUrl('public/avatar1.png') // data.publicUrl

// Private bucket — signed URL（expiresIn 單位是「秒」）
await supabase.storage.from('documents').createSignedUrl('doc.pdf', 3600, { download: 'report.pdf' })
await supabase.storage.from('documents').createSignedUrls(['a.pdf', 'b.pdf'], 3600)

// Signed UPLOAD URL — 讓 client 無金鑰上傳（有效 2h）
const { data } = await supabase.storage.from('user-uploads').createSignedUploadUrl('docs/report.pdf')
await supabase.storage.from('user-uploads').uploadToSignedUrl('docs/report.pdf', data.token, file, { contentType: 'application/pdf' })
```

影像轉換在 `getPublicUrl`/`createSignedUrl`/`download` 用 `transform: { width, height, resize: 'cover'|'fill'|'contain', quality, format }`。

### Storage RLS

Policy 寫在 **`storage.objects`**。關鍵欄位：`bucket_id`、`name`（路徑）。Helper `storage.foldername(name)` 回路徑各段的 `text[]`。權限：upload = INSERT、upsert = INSERT+SELECT+UPDATE、read = SELECT、delete = DELETE。

```sql
-- 每人專屬資料夾：路徑 "<uid>/file.png"
create policy "user folder read"
on storage.objects for select to authenticated
using ( bucket_id = 'my_bucket' and (storage.foldername(name))[1] = (select auth.uid()::text) );

create policy "user folder write"
on storage.objects for insert to authenticated
with check ( bucket_id = 'my_bucket' and (storage.foldername(name))[1] = (select auth.uid()::text) );

-- 公開讀
create policy "public read" on storage.objects for select using ( bucket_id = 'avatars' );
```

---

## 6. Edge Functions

Deno-based TypeScript，程式碼在 `supabase/functions/<name>/index.ts`。

```bash
supabase functions new hello-world      # 建立骨架
supabase functions serve hello-world    # 本地 /functions/v1/hello-world
supabase functions deploy hello-world   # 部署（省略 name = 全部）
```

### Handler — 現行 `Deno.serve`（舊的 `std/http` serve import 已淘汰）

```typescript
Deno.serve(async (req) => {
  const { name } = await req.json()
  return new Response(JSON.stringify({ message: `Hello ${name}!` }), {
    headers: { 'Content-Type': 'application/json' },
  })
})
```

### 函式內用 supabase-js + CORS + auth

```typescript
import { createClient } from 'npm:@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })
  try {
    // RLS-scoped 到呼叫者（轉發其 JWT）
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_ANON_KEY')!,
      { global: { headers: { Authorization: req.headers.get('Authorization')! } } },
    )
    const { data, error } = await supabase.from('users').select('*')
    if (error) throw error
    return new Response(JSON.stringify({ data }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 400 })
  }
})

// Admin（繞過 RLS）：用 SUPABASE_SERVICE_ROLE_KEY 取代轉發 Authorization header。
```

### Invoke

```javascript
const { data, error } = await supabase.functions.invoke('hello-world', {
  body: { name: 'JS' },
  method: 'POST',
})
// 型別化錯誤：FunctionsHttpError（4xx/5xx — 讀 error.context.json()）、
// FunctionsRelayError、FunctionsFetchError
```

### Secrets & 自動注入 env

```bash
supabase secrets set STRIPE_SECRET_KEY=sk_live_...
supabase secrets set --env-file ./supabase/functions/.env
supabase secrets list
# 本地：值放 supabase/functions/.env（functions serve 自動載入）
```

```typescript
const key = Deno.env.get('STRIPE_SECRET_KEY')
```

自動注入（免設定）：`SUPABASE_URL`、`SUPABASE_ANON_KEY`、`SUPABASE_SERVICE_ROLE_KEY`（繞過 RLS）、`SUPABASE_DB_URL`。JWT 驗證預設開 —— public/webhook 端點用 `--no-verify-jwt` 或 `config.toml` 的 `[functions.<name>] verify_jwt = false` 關閉。

---

## 7. Realtime

一條 WebSocket 上三種功能：**Postgres Changes**、**Broadcast**、**Presence**。

### Postgres Changes

```javascript
const channel = supabase
  .channel('db-todos')
  .on('postgres_changes',
    { event: '*', schema: 'public', table: 'todos', filter: 'id=eq.1' }, // event: INSERT|UPDATE|DELETE|*
    (payload) => console.log(payload)) // { eventType, new, old, schema, table }
  .subscribe()
```

Filter 運算子：`eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `in`。

**開 replication** —— 表必須在 publication 裡：

```sql
alter publication supabase_realtime add table public.todos;
```

- 受 RLS 限制 —— client 只收到 SELECT policy 允許的列的事件。
- UPDATE/DELETE payload 預設只含舊紀錄的 PK；要完整舊列：`alter table public.todos replica identity full;`（注意：replica identity full 時，DELETE 事件**不套用** RLS）。

### Broadcast

```javascript
const channel = supabase.channel('room-1')
channel
  .on('broadcast', { event: 'shout' }, (payload) => console.log(payload))
  .subscribe((status) => {
    if (status !== 'SUBSCRIBED') return
    channel.send({ type: 'broadcast', event: 'shout', payload: { message: 'Hi' } })
  })
// Config: { config: { broadcast: { self: true, ack: true } } }
```

> 大規模時 Supabase 現在建議 **Broadcast from Database**（DB trigger 呼叫 `realtime.broadcast_changes()` + `realtime.messages` 上的 RLS + client `await supabase.realtime.setAuth()`），優於 Postgres Changes。

### Presence

```javascript
const room = supabase.channel('room_01')
room
  .on('presence', { event: 'sync' },  () => console.log(room.presenceState()))
  .on('presence', { event: 'join' },  ({ key, newPresences })  => console.log('join', newPresences))
  .on('presence', { event: 'leave' }, ({ key, leftPresences }) => console.log('leave', leftPresences))
  .subscribe(async (status) => {
    if (status !== 'SUBSCRIBED') return
    await room.track({ user: 'user-1', online_at: new Date().toISOString() })
  })
// 穩定去重 key：supabase.channel('test', { config: { presence: { key: 'userId-123' } } })
```

### Cleanup

```javascript
supabase.removeChannel(channel)
supabase.removeAllChannels()
```

---

## 8. CLI & Local Development

### 安裝

```sh
brew install supabase/tap/supabase                    # macOS/Linux
scoop install supabase                                # Windows（先加 bucket）
npm install supabase --save-dev                       # 專案內（不支援 -g 全域）
npx supabase --help                                   # 臨時用
```

npx 需 Node 20+。`supabase --version` 驗證。

### Init, login, link

```sh
supabase init                              # 建立 supabase/（config.toml, migrations/, seed.sql）
supabase login                             # 瀏覽器認證（CI 用 export SUPABASE_ACCESS_TOKEN）
supabase link --project-ref <ref>
```

### 本地全套

```sh
supabase start    # 用 Docker 啟動全套
supabase status   # 印 URL / 金鑰 / 連線字串
supabase stop     # 停（--no-backup 連本地 DB volume 也清掉）
```

| 服務 | 埠 | | 服務 | 埠 |
|---|---|---|---|---|
| API gateway (Kong) | `54321` | | Postgres | `54322` |
| Studio | `54323` | | Inbucket/Mailpit（信件） | `54324` |

Auth、Storage、Realtime、PostgREST、Edge Runtime 都由 Kong 在 `54321` 前置。

### Migrations

```sh
supabase migration new create_employees    # 建時間戳 SQL 檔
supabase migration up                       # 套用未套用的到本地（保留資料）
supabase db reset                           # 清空 + 重跑所有 migration + seed.sql
supabase db push                            # 套用未套用的 migration 到 linked remote
supabase db push --include-seed
supabase db diff -f add_index               # 把 Studio 改動擷取成 migration
```

流程：`migration new` → 寫 SQL → `db reset` 測試 → commit → 由一人 `db push`。

### 產 TypeScript types

```sh
supabase gen types typescript --local             > src/database.types.ts
supabase gen types typescript --linked            > src/database.types.ts
supabase gen types typescript --project-id "$REF" > src/database.types.ts
```

```typescript
import { createClient } from '@supabase/supabase-js'
import { Database } from './database.types'
const supabase = createClient<Database>(url, publishableKey) // 查詢全程型別化
```

### Seeding & config

`supabase/seed.sql` 在每次 `supabase db reset`、跑完 migration 後執行。

```toml
# supabase/config.toml（改完 stop && start 套用）
project_id = "my-app"
[api]   port = 54321
[db]    port = 54322
[studio] port = 54323
[auth]  site_url = "http://localhost:3000"
[auth.external.github]
enabled = true
client_id = "env(GITHUB_CLIENT_ID)"   # 用 env() 從 .env 取 secret
secret    = "env(GITHUB_SECRET)"
```

---

## 9. Gotchas & Best Practices

- **`service_role` / `sb_secret_...` 金鑰絕不進前端** —— 它完全繞過 RLS。只放後端。
- **暴露的表一律開 RLS**（`public` schema 透過 PostgREST 可達）。沒開 = anon 能讀寫全部。RLS 在加 policy 前一律全拒。
- policy 用 `(select auth.uid())`（每語句快取，不是每列）。
- 真實專案用 **migration，不要點 dashboard** 改 schema —— 可審查、可重現、好 rollback。dashboard 改動用 `supabase db diff -f` 擷取。
- **select 指定欄位**，別 `select('*')`；大表加 `.limit()`/`.range()`。
- filter / join / RLS policy 用到的欄位**建索引**。
- 改完 schema **重新產 types**。

### Connection pooling — Supavisor（取代共用 PgBouncer）

| 方式 | 埠 | 模式 | 適合 |
|---|---|---|---|
| Direct connection | `5432` | — | 長壽 server（預設 IPv6；IPv4 為 add-on） |
| Supavisor session | `5432` | Session | 只有 IPv4 的常駐後端；可用 prepared statement |
| Supavisor transaction | `6543` | Transaction | **Serverless / edge / Lambda** |

```sh
# Direct
postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres
# Supavisor session (IPv4)
postgres://postgres.[REF]:[PASSWORD]@aws-[REGION].pooler.supabase.com:5432/postgres
# Supavisor transaction（serverless）← 埠 6543，username 帶 tenant
postgres://postgres.[REF]:[PASSWORD]@aws-[REGION].pooler.supabase.com:6543/postgres
```

- **Serverless/edge → transaction 模式、埠 6543。** 長壽 server → direct（5432）或 session 模式。
- **transaction 模式不支援 prepared statement** —— driver 要關（`prepare: false` / `?pgbouncer=true` 等）。
- transaction 模式的閒置連線約 5 分鐘被回收 —— 加重連/重試邏輯。
- direct 連線預設 **IPv6**；純 IPv4 網路走 pooler 或 IPv4 add-on。
- **歷史**：session 模式在 6543 已於 2025-02-28 棄用 —— **6543 = 只 transaction，5432 = session/direct**。
- 付費方案可用單租戶 **Dedicated Pooler（PgBouncer）** —— 只 transaction 模式、IPv6（或 IPv4 add-on）、更低延遲。

---

## 近期變動快速清單

1. **API 金鑰** —— `sb_publishable_...` / `sb_secret_...` 取代 `anon` / `service_role`。2025-11-01 起新專案只給新金鑰；舊金鑰預計 2026 底移除。走 `apikey` header，不是 Bearer。
2. **Server 端 auth** —— 授權用 `getClaims()` / `getUser()`，絕不用 `getSession()`。`@supabase/ssr` cookie 用 `getAll`/`setAll`（不是已淘汰的 `get`/`set`/`remove`）。
3. **Edge Functions** —— 用內建 `Deno.serve`（不是舊 `std/http` import）。
4. **Pooling** —— Supavisor 取代共用 PgBouncer；6543 只給 transaction。
