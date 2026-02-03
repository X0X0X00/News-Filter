# 网页分类 API 服务

基于 Qwen3-VL-Embedding 的网页分类服务，输入文章链接、标题、正文，返回 Top 2 分类标签。

## 文件结构

```
.
├── api_server.py                   # API 服务入口
├── requirements.txt                # Python 依赖
├── src/llm/
│   ├── embedding_classifier.py     # 分类器
│   └── qwen3_vl_embedding.py       # 嵌入模型封装
└── models/
    ├── hard_negative_train6000.pt   # 类别嵌入矩阵 (264KB)
    └── Qwen3-VL-Embedding-8B/      # 嵌入模型 (~16GB)
```

## 环境要求

- Python 3.10+
- CUDA GPU（至少 16GB 显存）
- 约 20GB 磁盘空间

## 安装与启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 如果 models/Qwen3-VL-Embedding-8B/ 不存在，需要下载模型
pip install huggingface_hub
huggingface-cli download Qwen/Qwen3-VL-Embedding-8B --local-dir models/Qwen3-VL-Embedding-8B

# 3. 启动服务 (FastAPI + uvicorn)
python api_server.py --port 8000
```

启动参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--host` | 0.0.0.0 | 监听地址 |
| `--port` | 8000 | 监听端口 |
| `--matrix` | models/hard_negative_train6000.pt | 类别嵌入矩阵路径 |
| `--model` | models/Qwen3-VL-Embedding-8B | 嵌入模型路径 |
| `--workers` | 1 | Worker 进程数 |

## 接口说明

### POST /classify

请求参数（JSON）：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `articleLink` | string | 否 | 文章链接 |
| `title` | string | 是* | 文章标题 |
| `text` | string | 是* | 文章正文 |

> `title` 和 `text` 至少提供一个。

请求示例：

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "articleLink": "https://example.com/news/12345",
    "title": "央行宣布降息",
    "text": "中国人民银行今日宣布下调贷款市场报价利率..."
  }'
```

返回示例：

```json
{
  "top2": [
    {"label": "经济", "score": 0.8712},
    {"label": "时政", "score": 0.7134}
  ]
}
```

### GET /health

健康检查接口。

```bash
curl http://localhost:8000/health
# 返回: {"status": "ok"}
```

## 分类类别

共 8 个类别：时政、经济、军事、社会、科技、体育、娱乐、其他。
