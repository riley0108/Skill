---
name: comfyui
description: 用 ComfyUI（節點式 AI 生成引擎，跑 Stable Diffusion / SDXL / SD3 / Flux 影像與 Wan/Hunyuan/LTX 影片、3D、音訊）的實作指南 —— 安裝啟動、節點圖原理、workflow JSON（UI 格式 vs API 格式）、HTTP/WebSocket API 程式化跑圖、自訂節點開發、ComfyUI-Manager 與 comfy-cli 生態。當使用者要「裝/跑 ComfyUI、用 API 自動跑 workflow、把 workflow 接進程式/n8n、改 prompt 與 seed 批量生成、寫 custom node、裝 custom node/模型、查 KSampler 參數、ControlNet/LoRA、數位人/對嘴影片走 ComfyUI 流程」時使用。附 repo 官方 API 範例腳本。
---

# 🟣 ComfyUI 實作指南

ComfyUI = 節點式（node graph）AI 生成引擎：把 Load Checkpoint → CLIP Text Encode → KSampler → VAE Decode → Save Image 等節點接成圖，後端執行。原生支援 SD1.5/SDXL/SD3.5/Flux 影像、Wan/Hunyuan/LTX/Mochi 影片、Hunyuan3D、音訊；也有 API nodes 接 Nano Banana / Seedance 等閉源模型。**對接你的數位人/對嘴影片技術棧**（RunComfy 上跑的就是這套；對嘴用 Hunyuan Avatar 等也走 ComfyUI workflow）。

完整可複製貼上程式碼在 **[references/reference.md](references/reference.md)**（7 大區）；repo 官方 API 範例已收進 **[scripts/](scripts/)**。

## 🗺️ reference.md 7 大區
1. **是什麼 & 安裝啟動** — Desktop app / Portable / `comfy-cli` / 手動 clone；啟動 flag（--listen / --port / --lowvram / --highvram / --cpu / --enable-cors-header）；`models/` 目錄擺放
2. **節點圖原理** — Load Checkpoint / CLIPTextEncode / KSampler / VAEDecode / SaveImage / LoraLoader / ControlNet；KSampler 參數；txt2img & img2img flow
3. **Workflow JSON：UI 格式 vs API 格式** ⭐ — 兩者差異與如何匯出 API 格式
4. **HTTP / WebSocket API** — `/prompt`、`/history`、`/view`、`/object_info`、`/upload/image`、`ws` 進度；完整 Python 跑圖範例
5. **自訂節點開發** — INPUT_TYPES / RETURN_TYPES / FUNCTION / NODE_CLASS_MAPPINGS；最小可跑範例
6. **ComfyUI-Manager & 生態** — Manager、comfy-cli 指令、Comfy Registry、模型來源
7. **實戰雷區**

## 🚀 30 秒起步
```bash
# 最省事的程式化安裝
pip install comfy-cli && comfy install && comfy launch
# 或手動
git clone https://github.com/comfyanonymous/ComfyUI && cd ComfyUI
pip install -r requirements.txt && python main.py
# 開放遠端 API 呼叫（要接 n8n / 外部程式時）
python main.py --listen 0.0.0.0 --port 8188 --enable-cors-header
```
預設服務在 `http://127.0.0.1:8188`。模型丟 `models/checkpoints`、LoRA 丟 `models/loras`、VAE 丟 `models/vae`、ControlNet 丟 `models/controlnet`；產出在 `output/`。

## 🤖 程式化跑圖（最常用 — 直接套 scripts/）
1. 在 UI 裡接好 workflow → **`File → Export Workflow (API)`** 匯出 **API 格式** JSON（舊版要先到 Settings 開「Enable Dev mode Options」才有「Save (API Format)」按鈕）。
2. 用 [scripts/basic_api_example.py](scripts/basic_api_example.py)（fire-and-forget，只 POST `/prompt`）或 [scripts/websockets_api_example.py](scripts/websockets_api_example.py)（等 WebSocket 進度、跑完抓圖）當骨架，改裡面的 `prompt[節點id]["inputs"]`：
```python
prompt["6"]["inputs"]["text"] = "你的正向 prompt"      # CLIPTextEncode 節點
import random
prompt["3"]["inputs"]["seed"] = random.randint(0, 2**32-1)  # KSampler 每次換 seed 才有變化
```
3. 跑完從 `/history/{prompt_id}` → `outputs[node_id]["images"]` 拿 filename/subfolder/type，再 `/view?...` 下載。需 `pip install websocket-client`。

## ☠️ 最容易踩的 5 個雷
1. **`/prompt` 只吃 API 格式，不吃 UI 格式** —— 直接丟 `File → Save` 的 workflow JSON 會驗證失敗。一定要匯出 **API 格式**（`File → Export Workflow (API)`）。
2. **Seed 不換 = 每次同一張圖** —— UI 的 `control_after_generate`（randomize）是前端 widget，**API JSON 裡沒有**，要自己 `random.randint` 換 seed。
3. **WebSocket「跑完」訊號 = `executing` 且 `node` 為 `null`、`prompt_id` 對得上** —— 要比對 `prompt_id`，否則會收到別人那次的事件。`client_id` 必須跟 WebSocket 的 `clientId` 一致才收得到自己的進度。
4. **節點 id 是契約** —— 程式用 `prompt["3"]` 之類引用節點，重新匯出可能被重新編號。改完要重核 id，或用 `_meta.title` / `class_type` 找。
5. **遠端/瀏覽器呼叫要 `--enable-cors-header`（+ `--listen 0.0.0.0` 對外）** —— 且 ComfyUI **沒有內建驗證**，對外開放要自己加保護（反向代理 + 認證）。

## 🔍 動態建/驗 workflow 的真相來源
`GET /object_info`（或 `/object_info/{class_type}`）回所有節點的合法 inputs、預設值、下拉枚舉（可用的 sampler/scheduler 名、已安裝的 checkpoint 清單）。要動態組或驗證 workflow 時查它，不要硬猜。

## 🧩 裝 custom node / 模型
- UI 內用 **ComfyUI-Manager**（`--enable-manager` 啟用）→「Install Custom Nodes」可裝節點、補 workflow 缺的節點、下載模型。
- CLI：`comfy node install <name>` / `comfy model download --url <URL> --relative-path models/checkpoints`。
- 手動：`git clone` 到 `custom_nodes/` 再重啟（有 `requirements.txt` 要先裝）。
- 模型來源：Hugging Face、Civitai（checkpoint/LoRA）；節點來源：Comfy Registry、GitHub。

> 來源：[comfyanonymous/ComfyUI](https://github.com/comfyanonymous/ComfyUI)（Comfy-Org 重導向至此）repo 的 `script_examples/` + [docs.comfy.org](https://docs.comfy.org)，核對於 2026-06。API 快速演進，動到時以官方文件再確認。
