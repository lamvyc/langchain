# 🚀 LangChain + RAG 最佳实践

一个完整的 LangChain + RAG（检索增强生成）学习项目，从零开始掌握构建知识库问答系统的核心技术。

## 📋 项目概述

本项目是一个循序渐进的学习教程，覆盖 RAG 系统的完整流程：

```
文档加载 → 文本分割 → 向量嵌入 → 向量存储 → 检索策略 → 问答生成 → 对话记忆
```

## 🛠️ 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| LLM | OpenAI GPT | 大语言模型 |
| Embedding | OpenAI Embeddings | 文本向量化 |
| Vector Store | Chroma | 轻量级本地向量数据库 |
| Framework | LangChain | LLM 应用开发框架 |
| 数据源 | PDF 文档 | 使用 PyPDF 解析 |

## 📁 项目结构

```
langchain-basic/
├── README.md                         # 项目说明文档
├── requirements.txt                  # Python 依赖列表
├── .env.example                      # 环境变量模板
├── .gitignore                        # Git 忽略配置
├── data/                             # 测试数据目录
│   └── README.md                     # 数据目录说明
├── 01_loaders/                       # 📄 文档加载器
│   └── pdf_loader.py                 # PDF 加载示例
├── 02_splitters/                     # ✂️ 文本分割器
│   └── text_splitter.py              # 分割策略示例
├── 03_embeddings/                    # 🔢 向量嵌入
│   └── embeddings_demo.py            # Embeddings 示例
├── 04_vectorstores/                  # 💾 向量存储
│   └── chroma_demo.py                # Chroma 数据库示例
├── 05_retrieval/                     # 🔍 检索策略
│   ├── similarity_search.py          # 相似度搜索
│   ├── mmr_search.py                 # MMR 搜索
│   └── metadata_filter.py            # 元数据过滤
├── 06_qa_chain/                      # 💬 问答链
│   └── retrieval_qa.py               # RetrievalQA 示例
└── 07_conversational/                # 🗣️ 对话式RAG
    └── conversational_chain.py       # 对话链示例
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+（推荐 3.11+）
- OpenAI API Key

### 2. 安装依赖

```bash
# 克隆项目
cd langchain-basic

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 OpenAI API Key
OPENAI_API_KEY=sk-your-api-key-here
```

### 4. 准备测试数据

将你的 PDF 文档放入 `data/` 目录中。

### 5. 运行示例

```bash
# 按顺序学习每个模块
python 01_loaders/pdf_loader.py
python 02_splitters/text_splitter.py
python 03_embeddings/embeddings_demo.py
# ... 以此类推
```

## 📚 学习路径

### Week 1：基础篇
| 模块 | 内容 | 学习目标 |
|------|------|----------|
| 01_loaders | 文档加载器 | 掌握 PDF 文档的加载与解析 |
| 02_splitters | 文本分割器 | 理解分割策略对检索效果的影响 |

### Week 2：核心篇
| 模块 | 内容 | 学习目标 |
|------|------|----------|
| 03_embeddings | 向量嵌入 | 理解文本向量化原理 |
| 04_vectorstores | 向量存储 | 掌握 Chroma 向量数据库使用 |
| 05_retrieval | 检索策略 | 掌握相似度搜索、MMR、元数据过滤 |

### Week 3：进阶篇
| 模块 | 内容 | 学习目标 |
|------|------|----------|
| 06_qa_chain | 问答链 | 构建完整的 RAG 问答流程 |
| 07_conversational | 对话式RAG | 实现带记忆的多轮对话系统 |

## 🔑 核心概念

### RAG 流程图

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  文档加载    │ -> │  文本分割    │ -> │  向量嵌入    │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              v
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  生成答案    │ <- │  构建提示    │ <- │  向量存储    │
└─────────────┘    └─────────────┘    └─────────────┘
       ^                                      │
       │           ┌─────────────┐            │
       └────────── │  相关检索    │ <──────────┘
                   └─────────────┘
                          ^
                          │
                   ┌─────────────┐
                   │  用户查询    │
                   └─────────────┘
```

## 📖 参考资源

- [LangChain 官方文档](https://python.langchain.com/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Chroma 文档](https://docs.trychroma.com/)
- [DeepLearning.AI - LangChain Chat with Your Data](https://learn.deeplearning.ai/courses/langchain-chat-with-your-data)

## 📝 License

MIT License