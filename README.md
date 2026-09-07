# 掌柜智库 (Knowledge Base 0525)

一个基于 LangGraph 构建的智能知识库系统，支持文档导入、向量化存储和智能问答。通过 PDF 文档解析、多路召回、混合检索和重排序技术，提供高质量的知识检索和问答服务。

## 核心特性

- **智能文档处理**：基于 MinerU 的 PDF 转 Markdown 能力，保留文档结构和图片信息
- **混合检索架构**：结合稠密向量、稀疏向量、HyDE 假设性检索和 Web 搜索的多路召回
- **商品名识别**：自动提取文档中的商品/产品名称，实现精准过滤
- **流式问答**：支持 SSE 流式输出，实时返回生成结果
- **LangGraph 编排**：使用有向无环图编排复杂的导入和查询流程，可视化节点执行状态

## 技术架构

### 核心技术栈

- **框架**：FastAPI + LangGraph
- **向量模型**：BGE-M3（BAAI）混合向量检索
- **重排序**：BGE-Reranker-Large
- **向量数据库**：Milvus
- **对象存储**：MinIO
- **文档解析**：MinerU
- **大模型**：阿里云 DashScope（Qwen 系列）

### 系统架构

```
┌─────────────┐
│  前端页面    │  chat.html / import.html
└──────┬──────┘
       │
┌──────▼───────────────────────────────────┐
│        FastAPI 服务层                     │
│  ┌────────────────┐  ┌─────────────────┐ │
│  │ 导入服务(8000)  │  │ 查询服务(8001)   │ │
│  │ import_service │  │ query_service   │ │
│  └────────┬───────┘  └────────┬────────┘ │
└───────────┼──────────────────┼──────────┘
            │                  │
┌───────────▼──────────┐  ┌───▼───────────────┐
│ 导入处理流程(LangGraph)│  │ 查询处理流程       │
│                      │  │  (LangGraph)      │
│ ┌──────────────────┐ │  │ ┌───────────────┐ │
│ │ Entry            │ │  │ │ 商品名确认     │ │
│ │ PDF → MD         │ │  │ │ 向量检索       │ │
│ │ 图片处理         │ │  │ │ HyDE 检索      │ │
│ │ 文档切分         │ │  │ │ Web 搜索       │ │
│ │ 商品名识别       │ │  │ │ RRF 融合       │ │
│ │ BGE 向量化       │ │  │ │ 重排序         │ │
│ │ 导入 Milvus      │ │  │ │ 答案生成       │ │
│ └──────────────────┘ │  │ └───────────────┘ │
└──────────────────────┘  └────────────────────┘
            │                      │
┌───────────▼──────────────────────▼─────────┐
│           底层服务                          │
│  ┌────────┐ ┌────────┐ ┌──────┐ ┌──────┐ │
│  │ Milvus │ │ MinIO  │ │ LLM  │ │MongoDB│ │
│  └────────┘ └────────┘ └──────┘ └──────┘ │
└────────────────────────────────────────────┘
```

## 项目结构

```
knowledge_base_0525/
├── config/                        # 配置文件
│   ├── embedding_config.py        # 向量模型配置
│   ├── lm_config.py              # 大模型配置
│   ├── milvus_config.py          # Milvus 配置
│   ├── mineru_config.py          # MinerU 配置
│   ├── minio_config.py           # MinIO 配置
│   └── rerank_config.py          # 重排序配置
│
├── processor/                     # 业务流程（LangGraph）
│   ├── import_processor/         # 导入流程
│   │   ├── base.py              # 节点基类
│   │   ├── main_graph.py        # 流程图定义
│   │   ├── state.py             # 状态定义
│   │   └── nodes/               # 处理节点
│   │       ├── a_node_entry.py              # 入口节点
│   │       ├── b_node_pdf_to_md.py          # PDF 转 Markdown
│   │       ├── c_node_md_img.py             # 图片处理
│   │       ├── d_node_document_split.py     # 文档切分
│   │       ├── e_node_item_name_recognition.py  # 商品识别
│   │       ├── f_node_bge_embedding.py      # 向量嵌入
│   │       └── g_node_import_milvus.py      # 存储到 Milvus
│   │
│   └── query_processor/          # 查询流程
│       ├── base.py              # 节点基类
│       ├── main_graph.py        # 流程图定义
│       ├── state.py             # 状态定义
│       ├── prompt/              # 提示词模板
│       └── nodes/               # 处理节点
│           ├── a_node_item_name_confirm.py  # 商品名确认
│           ├── b_node_search_embedding.py   # 向量检索
│           ├── c_node_search_embedding_hyde.py  # HyDE 检索
│           ├── d_node_web_search_mcp.py     # Web 搜索
│           ├── e_node_rrf.py                # RRF 融合
│           ├── f_node_rerank.py             # 重排序
│           └── g_node_answer_output.py      # 答案生成
│
├── web/                          # Web 服务
│   ├── api/                     # API 接口
│   │   ├── import_service.py   # 导入服务 (8000)
│   │   └── query_service.py    # 查询服务 (8001)
│   └── page/                    # 前端页面
│       ├── chat.html           # 聊天界面
│       └── import.html         # 导入界面
│
├── utils/                        # 工具函数
│   ├── embedding_utils.py       # 向量嵌入
│   ├── llm_utils.py            # LLM 客户端
│   ├── milvus_utils.py         # Milvus 操作
│   ├── minio_utils.py          # MinIO 操作
│   ├── mongo_history_utils.py  # MongoDB 历史记录
│   ├── reranker_http_utils.py  # 重排序服务
│   ├── sse_utils.py            # SSE 流式推送
│   └── task_utils.py           # 任务状态管理
│
├── tool/                         # 辅助工具
│   ├── download_bgem3.py        # 下载 BGE-M3 模型
│   └── logger.py                # 日志工具
│
├── test/                         # 测试代码
├── .env                          # 环境配置
├── .env.example                  # 配置模板
└── README.md                     # 本文档
```

## 快速开始

### 1. 环境准备

#### 创建 Python 环境

```bash
# 使用 conda
conda create -n py311 python=3.11
conda activate py311

# 或使用 venv
python -m venv kb311
.\kb311\Scripts\activate  # Windows
source kb311/bin/activate  # Linux/Mac
```

#### 安装 PyTorch（根据 CUDA 版本选择）

```bash
# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# CUDA 12.4
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# CUDA 12.6 (RTX 5090)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126

# 验证安装
python -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
```

#### 安装核心依赖

```bash
# 安装 MinerU（PDF 解析）
pip install --upgrade pip
pip install uv
uv pip install -U "mineru[all]"
mineru --version

# 下载 MinerU 模型
$env:MODELSCOPE_CACHE="D:\ai_models\modelscope_cache"  # Windows
mineru-models-download

# 安装向量模型依赖
pip install "pymilvus[model]" transformers FlagEmbedding

# 安装 FastAPI
pip install fastapi "uvicorn[standard]"
```

### 2. 下载模型

#### BGE-M3 向量模型

```python
# 执行 tool/download_bgem3.py
from modelscope.hub.snapshot_download import snapshot_download

model_dir = snapshot_download(
    'BAAI/bge-m3', 
    cache_dir='D:/ai_models/modelscope_cache/models'
)
print(f"模型已下载到: {model_dir}")
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，修改以下关键配置：

```bash
# MinerU API
MINERU_API_TOKEN=your_token
MINERU_BASE_URL=https://mineru.net/api/v4

# 模型路径
MODELSCOPE_CACHE=D:/ai_models/modelscope_cache
BGE_M3_PATH=D:/ai_models/modelscope_cache/models/BAAI/bge-m3
BGE_RERANKER_LARGE=D:/ai_models/modelscope_cache/models/BAAI/bge-reranker-large

# 阿里云 DashScope
OPENAI_API_KEY=sk-your-api-key
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_DEFAULT_MODEL=qwen-flash

# Milvus
MILVUS_URL=http://localhost:19530
CHUNKS_COLLECTION=kb_chunks
ITEM_NAME_COLLECTION=kb_item_names

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=knowledge-base

# MongoDB
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=kb001
```

### 4. 启动服务

#### 启动 Milvus

```bash
docker run -d --name milvus \
  -p 19530:19530 \
  -p 9091:9091 \
  milvusdb/milvus:latest
```

#### 启动 MinIO

```bash
docker run -d --name minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

#### 启动 MongoDB

```bash
docker run -d --name mongodb \
  -p 27017:27017 \
  mongo:latest
```

#### 启动应用服务

```bash
# 终端 1：启动导入服务
python web/api/import_service.py
# 访问：http://localhost:8000/import.html

# 终端 2：启动查询服务
python web/api/query_service.py
# 访问：http://localhost:8001/chat.html
```

## 使用说明

### 文档导入

1. 访问 `http://localhost:8000/import.html`
2. 上传 PDF 文档
3. 系统自动执行导入流程：
   - PDF 转 Markdown（MinerU）
   - 提取图片并处理
   - 文档切分（RecursiveCharacterTextSplitter）
   - 商品名识别（LLM）
   - 向量化（BGE-M3）
   - 存储到 Milvus

### 知识问答

1. 访问 `http://localhost:8001/chat.html`
2. 输入问题
3. 系统执行查询流程：
   - 商品名确认（提取用户问题中的商品关键词）
   - 多路召回：
     - 普通向量检索（BGE-M3 稠密+稀疏）
     - HyDE 假设性检索
     - Web 搜索（可选）
   - RRF 融合排序
   - 重排序（BGE-Reranker）
   - 答案生成（LLM 流式输出）

### API 接口

#### 导入接口

```bash
# 上传文件
curl -X POST http://localhost:8000/upload \
  -F "files=@document.pdf"

# 查询任务状态
curl http://localhost:8000/status/{task_id}
```

#### 查询接口

```bash
# 非流式查询
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "华为B730显示器如何安装？",
    "session_id": "test_session",
    "is_stream": false
  }'

# 流式查询
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "华为B730显示器如何安装？",
    "session_id": "test_session",
    "is_stream": true
  }'

# 获取流式结果
curl -N http://localhost:8001/stream/test_session
```

## 核心流程说明

### 导入流程（KBImportWorkflow）

```
START
  ↓
Entry Node (判断文件类型)
  ↓
PDF → Markdown (MinerU 转换)
  ↓
MD Image Processing (图片提取与上下文标注)
  ↓
Document Split (文档切分，chunk_size=800)
  ↓
Item Name Recognition (商品名识别)
  ↓
BGE Embedding (稠密+稀疏向量生成)
  ↓
Import to Milvus (向量存储)
  ↓
END
```

### 查询流程（KBQueryWorkflow）

```
START
  ↓
Item Name Confirm (提取商品名)
  ↓
  ├─→ Search Embedding (普通向量检索)
  ├─→ Search HyDE (假设性文档检索)
  └─→ Web Search MCP (网络搜索)
  ↓
RRF Fusion (倒数排名融合)
  ↓
Rerank (BGE-Reranker 重排序)
  ↓
Answer Output (LLM 生成答案)
  ↓
END
```

## 常见问题

### 1. PyTorch CUDA 不可用

```bash
# 检查 CUDA 版本
nvidia-smi

# 重装匹配的 PyTorch
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 2. TensorFlow 与 transformers 冲突

```bash
# 方案1：安装 tf-keras
pip install tf-keras

# 方案2：卸载 TensorFlow
pip uninstall tensorflow keras tf-keras -y
```

### 3. MinerU 模型下载失败

```bash
# 设置镜像源
pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple

# 手动下载
# 访问：https://mineru.net/ 下载桌面客户端
```

### 4. Milvus 连接失败

```bash
# 检查 Milvus 是否启动
docker ps | grep milvus

# 查看日志
docker logs milvus
```

## 技术亮点

1. **LangGraph 流程编排**：使用有向无环图编排复杂的多步骤流程，支持条件路由和并行执行
2. **混合向量检索**：BGE-M3 同时生成稠密向量和稀疏向量，提升召回率
3. **HyDE 技术**：生成假设性答案文档，通过向量检索找到相似的真实文档
4. **RRF 融合**：倒数排名融合多路召回结果，平衡不同检索方式的权重
5. **商品名过滤**：自动识别文档中的商品名，实现精准的领域过滤
6. **流式输出**：SSE 推送实时生成内容，提升用户体验

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，欢迎提交 Issue。
