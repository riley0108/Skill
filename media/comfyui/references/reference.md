# ComfyUI Reference (2026)

> 節點式 AI 生成引擎。核對於 docs.comfy.org + repo `script_examples/`，2026-06。官方 API 範例腳本已收進本 skill 的 [`../scripts/`](../scripts/)。

---

## 1. 是什麼 & 安裝啟動

**是什麼**：節點圖（visual dataflow）介面，把模型載入器、prompt 編碼器、sampler、解碼器等節點接成圖，後端執行。Repo：`github.com/comfyanonymous/ComfyUI`（org `Comfy-Org` 重導向至此）。

**支援模型**：
- **影像**：SD1.x、SD2.x、SDXL、SD3/SD3.5、Flux、Flux 2
- **影片**：Stable Video Diffusion、Mochi、LTX-Video、Hunyuan Video、Wan 2.1/2.2
- **3D**：Hunyuan3D 2.0｜**音訊**：Stable Audio、ACE Step

### 安裝選項

**A) ComfyUI Desktop** — 一鍵安裝 app（Windows/macOS），最簡單，含 server + 前端。

**B) ComfyUI Portable（Windows）** — 下載 GPU 對應的 7z 解壓，跑 bat：
```
run_nvidia_gpu.bat     # Nvidia
run_amd_gpu.bat        # AMD
run_cpu.bat            # CPU only
```
要加 flag 就編輯 `.bat`（例：append `--listen`）。

**C) comfy-cli（推薦 CLI）**：
```bash
pip install comfy-cli
comfy install            # clone ComfyUI + 裝依賴到當前目錄
comfy launch             # 啟動 server
comfy launch -- --listen 0.0.0.0 --port 8188   # flag 放 `--` 之後
```

**D) 手動（git clone）**：
```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
python main.py
```
預設 server：`http://127.0.0.1:8188`。

### 啟動 flag（`comfy/cli_args.py`）

| Flag | 作用 |
|---|---|
| `--listen [IP]` | 綁定位址（預設 `127.0.0.1`；對外用 `0.0.0.0`） |
| `--port N` | 連接埠（預設 `8188`） |
| `--cpu` | 全部跑 CPU（慢，最後手段） |
| `--lowvram` | 拆分模型；text encoder 可能跑 CPU |
| `--normalvram` | 強制 normal VRAM 模式 |
| `--highvram` | 模型常駐 GPU VRAM（不卸載） |
| `--novram` | 最激進卸載（極低 VRAM） |
| `--gpu-only` | 全部存放並執行於 GPU |
| `--cpu-vae` | VAE 跑 CPU（VAE decode OOM 時用） |
| `--enable-cors-header [ORIGIN]` | 送 CORS header（遠端/瀏覽器 API 呼叫必需） |
| `--max-upload-size MB` | 上傳上限（預設 100 MB） |
| `--preview-method auto\|taesd\|latent2rgb` | sampler 即時預覽 |
| `--enable-manager` | 啟用內建 ComfyUI-Manager |
| `--disable-api-nodes` | 關閉 hosted API nodes |
| `--tls-keyfile / --tls-certfile` | 走 HTTPS |

### 模型擺放（`ComfyUI/models/`）
```
models/checkpoints/      # 完整 SD/SDXL/SD3/Flux checkpoint (.safetensors/.ckpt)
models/loras/            # LoRA / LyCORIS
models/vae/              # 獨立 VAE
models/controlnet/       # ControlNet
models/clip/  models/text_encoders/   # 文字編碼器（Flux/SD3 的 CLIP-L、T5）
models/clip_vision/      # CLIP vision（IP-Adapter 等）
models/diffusion_models/ (unet/)      # 獨立 UNet / diffusion 權重
models/embeddings/       # textual-inversion
models/upscale_models/   # ESRGAN 類放大
models/style_models/     # style adapter
```
產出在 `output/`、輸入在 `input/`。共用/額外模型路徑用 `extra_model_paths.yaml` 對應。

---

## 2. 節點圖原理

| 節點（`class_type`） | 角色 |
|---|---|
| **Load Checkpoint**（`CheckpointLoaderSimple`） | 載 checkpoint，輸出 `MODEL`、`CLIP`、`VAE` |
| **CLIP Text Encode (Prompt)**（`CLIPTextEncode`） | prompt → `CONDITIONING`（正向/負向各一） |
| **Empty Latent Image**（`EmptyLatentImage`） | 空白 latent：`width`/`height`/`batch_size` |
| **KSampler**（`KSampler`） | 去噪 sampler（跑 diffusion） |
| **VAE Decode**（`VAEDecode`） | latent → 像素影像 |
| **VAE Encode**（`VAEEncode`） | 影像 → latent（img2img） |
| **Save Image**（`SaveImage`） | 寫 PNG 到 `output/`，帶 `filename_prefix` |
| **Load Image**（`LoadImage`） | 從 `input/` 載圖 |
| **LoraLoader** | 套 LoRA，patch `MODEL` + `CLIP` |
| **ControlNetLoader** + **ControlNetApply** | 加 ControlNet 引導 |
| **Upscale**（`ImageUpscaleWithModel` / `LatentUpscale`） | 放大 |

**KSampler 參數**：
- `seed` — RNG 種子（換它才有不同結果）
- `steps` — 去噪步數（例 20–30）
- `cfg` — classifier-free guidance（prompt 貼合度，例 7–8）
- `sampler_name` — 例 `euler`、`dpmpp_2m`、`dpmpp_2m_sde`
- `scheduler` — 例 `normal`、`karras`、`exponential`、`sgm_uniform`
- `denoise` — 0.0–1.0；txt2img 用 `1.0`，img2img 用較低（例 0.5–0.75）

**txt2img flow**：
```
Load Checkpoint ─MODEL──────────────────────┐
                ├─CLIP─ CLIP Text Encode(+) ─CONDITIONING(positive)─┐
                ├─CLIP─ CLIP Text Encode(-) ─CONDITIONING(negative)─┤
                └─VAE──────────────────────┐                       │
Empty Latent Image ─LATENT─────────────────┼──> KSampler ─LATENT──> VAE Decode ─IMAGE──> Save Image
                                            └─MODEL ─────┘
```
**img2img flow**：把 `Empty Latent Image` 換成 `Load Image → VAE Encode → LATENT` 接進 KSampler，並把 `denoise` 設 < 1.0。

---

## 3. Workflow JSON：UI 格式 vs API 格式

兩種序列化：
- **UI / 完整 workflow 格式** — `File → Save` 產生、編輯器載入的。含 `nodes`、`links`、節點**位置/尺寸/顏色/群組**、widget 佈局。**不能直接餵 `/prompt`**。
- **API 格式** — `File → Export Workflow (API)` 匯出（舊版：開 dev mode → **「Save (API Format)」**）。扁平物件、**以節點 id 為 key**，每筆有 `class_type` + `inputs`（+ 選用 `_meta`）。UI metadata 被剝除。**這是 `/prompt` 要的格式。**

**API 格式節點結構**（連線是 `[來源節點id, 輸出index]` 陣列）：
```json
{
  "3": {
    "inputs": {
      "seed": 156680208700286,
      "steps": 20,
      "cfg": 8,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    },
    "class_type": "KSampler",
    "_meta": { "title": "KSampler" }
  }
}
```

**開啟 API 匯出**：
- 新版前端：**`File → Export Workflow (API)`** 直接下載 `.json`。
- 舊版：**Settings（齒輪）** → 開 **「Enable Dev mode Options」** → 右上選單出現 **「Save (API Format)」**。

---

## 4. HTTP / WebSocket API

Server 預設 `http://127.0.0.1:8188`。

| Method / Path | 用途 |
|---|---|
| `POST /prompt` | 排入 **API 格式** workflow。Body `{"prompt": {...}, "client_id": "..."}`。回 `{"prompt_id","number","node_errors"}` |
| `GET /history` | 全部完成歷史 |
| `GET /history/{prompt_id}` | 單次結果（含 `outputs` → 各節點 `images` 的 `filename`/`subfolder`/`type`） |
| `GET /view?filename=&subfolder=&type=` | 抓輸出檔（`type` = `output`/`input`/`temp`） |
| `POST /upload/image` | 上傳影像（multipart）到 `input/` |
| `GET /object_info` | 所有節點 schema（inputs/outputs/預設） |
| `GET /object_info/{class_type}` | 單一節點 schema |
| `GET /queue` | 目前佇列（執行中 + 等待） |
| `POST /interrupt` | 中止當前執行 |
| `GET /embeddings` | 可用 embedding 名 |
| `GET /system_stats` | Python 版本、裝置、VRAM |
| `ws://host/ws?clientId=<id>` | 執行事件 WebSocket |

**WebSocket 訊息類型**（JSON；binary frame 是 latent 預覽）：
- `status` — `data.status.exec_info.queue_remaining`
- `execution_start` — `{prompt_id}`
- `execution_cached` — `{prompt_id, nodes:[...]}`（快取命中的節點）
- `executing` — `{node, prompt_id}`；**`node` 為 `null` 且 `prompt_id` 相符 = 跑完**
- `progress` — `{node, prompt_id, value, max}`（單步進度）
- `executed` — `{node, prompt_id, output}`（節點回 UI 資料，如影像）
- `execution_error` — `{prompt_id, ...}`

連線的 `clientId` **必須等於** POST `/prompt` 的 `client_id`，否則收不到那次的事件。

### 完整 Python 範例

`scripts/websockets_api_example.py`（等 WebSocket 跑完抓圖）與 `scripts/basic_api_example.py`（只 POST、fire-and-forget）即 repo 官方範例，已收進本 skill。核心 pattern：

```python
import websocket, uuid, json, urllib.request, urllib.parse  # pip install websocket-client
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    req = urllib.request.Request("http://{}/prompt".format(server_address),
                                 data=json.dumps(p).encode('utf-8'))
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    q = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": folder_type})
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, q)) as r:
        return r.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as r:
        return json.loads(r.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    while True:                                  # 等跑完
        out = ws.recv()
        if isinstance(out, str):
            m = json.loads(out)
            if m['type'] == 'executing' and m['data']['node'] is None \
               and m['data']['prompt_id'] == prompt_id:
                break
        else:
            continue                             # binary = 預覽，略過
    images = {}
    history = get_history(prompt_id)[prompt_id]
    for node_id, node_output in history['outputs'].items():
        if 'images' in node_output:
            images[node_id] = [get_image(i['filename'], i['subfolder'], i['type'])
                               for i in node_output['images']]
    return images

ws = websocket.WebSocket()
ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
# prompt = json.loads(open("workflow_api.json").read())
# prompt["6"]["inputs"]["text"] = "你的 prompt"
# prompt["3"]["inputs"]["seed"] = random.randint(0, 2**32-1)
# images = get_images(ws, prompt)
ws.close()
```

若 workflow 含 hosted **API nodes**，在 payload 加 `extra_data.api_key_comfy_org`（key 在 platform.comfy.org 產）。

---

## 5. 自訂節點開發

custom node 是一個 Python class。最小完整範例：

```python
class ImageSelector:
    CATEGORY = "example"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": { "images": ("IMAGE",) },
            "optional": { "index": ("INT", {"default": 0, "min": 0, "max": 64}) },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)      # 選用；預設用型別名
    FUNCTION = "choose_image"      # 要呼叫的方法名

    def choose_image(self, images, index=0):
        # images 是 torch tensor batch [B, H, W, C]
        return (images[index].unsqueeze(0),)   # 必須回 tuple

# 註冊 — ComfyUI 啟動時讀取
NODE_CLASS_MAPPINGS = { "ImageSelector": ImageSelector }
NODE_DISPLAY_NAME_MAPPINGS = { "ImageSelector": "Image Selector" }
```

契約：
- `INPUT_TYPES` — classmethod 回 `{"required": {...}, "optional": {...}}`；每個 input 是 `(TYPE,)` 或 `(TYPE, {options})`。型別：`IMAGE`/`LATENT`/`MODEL`/`CLIP`/`VAE`/`CONDITIONING`/`INT`/`FLOAT`/`STRING`/`BOOLEAN`，或給 list 做下拉。
- `RETURN_TYPES` — 輸出型別 tuple。`RETURN_NAMES` — 選用標籤。
- `FUNCTION` — 被呼叫的方法名；必須回**符合 `RETURN_TYPES` 的 tuple**（或回含 `ui`/`result` 的 dict 送 UI 資料）。
- `CATEGORY` — 選單位置。選用 `OUTPUT_NODE = True`（終端節點）、`@classmethod IS_CHANGED(...)`（快取控制）。

**檔案/套件結構** — 放 `ComfyUI/custom_nodes/<your_node>/`。套件 `__init__.py` 要 export mapping：
```python
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
# 選用 JS 前端擴充：WEB_DIRECTORY = "./web/js"
```

**安裝方式**：ComfyUI-Manager（UI「Install Custom Nodes」）、`git clone` 到 `custom_nodes/` 後重啟（有 `requirements.txt` 先裝）、或 `comfy node install <name>`。

---

## 6. ComfyUI-Manager & 生態

**ComfyUI-Manager** = UI 內套件管理：裝/更新/停用 custom node、補 workflow 缺的節點、下載模型。`--enable-manager` 啟用內建版。

**Comfy Registry** — 官方 custom node 索引（驅動 Manager）：語意化**版本**（workflow JSON 記版本，可重現）、**安全掃描**（惡意 pip wheel / syscall；通過者有勾勾）、搜尋；已發布版本不可變。

**comfy-cli 指令**：
```bash
pip install comfy-cli
comfy install                          # 裝 ComfyUI
comfy launch                           # 跑 server
comfy launch -- --listen 0.0.0.0       # 傳遞啟動 flag
comfy node install <NODE_NAME>         # 從 registry 裝 custom node
comfy node update all
comfy model download --url <URL> --relative-path models/checkpoints
comfy generate ...                     # 呼叫 hosted partner nodes（Flux/Ideogram/DALL·E）
```

**模型/節點來源**：Hugging Face、Civitai（checkpoint/LoRA）；Comfy Registry、GitHub（custom node）。

---

## 7. 實戰雷區

- **`/prompt` 只吃 API 格式，不吃 UI 格式** —— 丟 `File → Save` 的 workflow 會驗證失敗。一律 `File → Export Workflow (API)`。
- **節點 id 是契約** —— 程式用 id 引用節點；重新匯出可能重新編號，改完重核 id 或用 `class_type`/`_meta.title` 找。
- **Seed = 變化** —— 同 seed 重現同圖；要新結果就 `random.randint(0, 2**32-1)`。UI 的 `control_after_generate` 是前端 widget，**API JSON 沒有**，要自己換 seed。
- **`executing` 且 `node: null` + `prompt_id` 相符 = 跑完**。比對 `prompt_id` 才不會誤判別人的 run。
- **`client_id` 要等於 WebSocket `clientId`** 才收得到自己的事件。
- **抓輸出**：`/history/{prompt_id}` → `outputs[node_id]["images"]` → 每個有 `filename`/`subfolder`/`type` → `/view?filename=...&subfolder=...&type=output` 下載。
- **VRAM flag 影響大**：小卡 `--lowvram` / `--novram`；要快取模型 `--highvram`；最後手段 `--cpu`；VAE OOM 用 `--cpu-vae`。
- **遠端/瀏覽器呼叫**需 `--enable-cors-header`（+ `--listen 0.0.0.0` 對外）。**無內建驗證**，對外要自己加保護。
- **輸出**在 `output/`（依 `SaveImage` 的 `filename_prefix`，如 `ComfyUI_00001_.png`）；`temp/` 預覽；上傳到 `input/`。
- **`GET /object_info`** 是合法 `class_type`、input 名、預設值、下拉枚舉（sampler/scheduler 名、可用 checkpoint）的真相來源 —— 動態組/驗 workflow 查它。
- POST 大圖到 `/upload/image` 時調高 `--max-upload-size`。

---

**主要來源**：`script_examples/websockets_api_example.py`、`basic_api_example.py`、`comfy/cli_args.py`（comfyanonymous/ComfyUI）；docs.comfy.org 的 Workflow API Format / server comms / custom node walkthrough / comfy-cli / Registry 頁。
