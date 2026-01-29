# LangChain + RAG 最佳实践项目 - 执行计划

## 项目概述
- **目标**：搭建一个完整的 LangChain + RAG 学习项目，覆盖从文档加载到对话式问答的全流程
- **技术栈**：Python 3.13.5 + LangChain + OpenAI + Chroma + PDF文档
- **预计文件数**：约 15 个文件

---

## 执行计划

### 第一阶段：项目基础配置

- [x] **1.1 创建项目说明文件**
  - 文件：`README.md`
  - 操作：新增
  - 目标：项目介绍、目录结构说明、快速开始指南

- [x] **1.2 创建依赖配置文件**
  - 文件：`requirements.txt`
  - 操作：新增
  - 目标：列出所有 Python 依赖包（langchain、openai、chromadb、pypdf 等）

- [x] **1.3 创建环境变量模板**
  - 文件：`.env.example`
  - 操作：新增
  - 目标：OpenAI API Key 配置模板

- [x] **1.4 创建 Git 忽略文件**
  - 文件：`.gitignore`
  - 操作：新增
  - 目标：忽略 .env、__pycache__、chroma_db 等文件

- [x] **1.5 创建测试数据目录**
  - 目录：`data/`
  - 操作：新增
  - 目标：存放 PDF 测试文档，附带 README 说明

---

### 第二阶段：文档加载器（Loaders）

- [x] **2.1 创建 PDF 加载器示例**
  - 文件：`01_loaders/pdf_loader.py`
  - 操作：新增
  - 目标：演示如何使用 PyPDFLoader 加载 PDF 文档，提取文本内容和元数据

---

### 第三阶段：文本分割器（Splitters）

- [x] **3.1 创建文本分割器示例**
  - 文件：`02_splitters/text_splitter.py`
  - 操作：新增
  - 目标：演示 CharacterTextSplitter 和 RecursiveCharacterTextSplitter 的区别与使用

---

### 第四阶段：向量嵌入（Embeddings）

- [x] **4.1 创建嵌入模型示例**
  - 文件：`03_embeddings/embeddings_demo.py`
  - 操作：新增
  - 目标：演示如何使用 OpenAI Embeddings 将文本转换为向量

---

### 第五阶段：向量存储（Vector Stores）

- [x] **5.1 创建 Chroma 向量数据库示例**
  - 文件：`04_vectorstores/chroma_demo.py`
  - 操作：新增
  - 目标：演示如何创建向量数据库、存储文档向量、持久化存储

---

### 第六阶段：检索策略（Retrieval）

- [x] **6.1 创建相似度搜索示例**
  - 文件：`05_retrieval/similarity_search.py`
  - 操作：新增
  - 目标：演示基础的相似度搜索方法

- [x] **6.2 创建 MMR 搜索示例**
  - 文件：`05_retrieval/mmr_search.py`
  - 操作：新增
  - 目标：演示最大边际相关（MMR）搜索，平衡相关性与多样性

- [x] **6.3 创建元数据过滤示例**
  - 文件：`05_retrieval/metadata_filter.py`
  - 操作：新增
  - 目标：演示如何使用元数据进行精确过滤

---

### 第七阶段：问答链（QA Chain）

- [x] **7.1 创建 RetrievalQA 示例**
  - 文件：`06_qa_chain/retrieval_qa.py`
  - 操作：新增
  - 目标：演示完整的 RAG 问答流程，从检索到生成答案

---

### 第八阶段：对话式 RAG（Conversational RAG）

- [x] **8.1 创建对话式检索链示例**
  - 文件：`07_conversational/conversational_chain.py`
  - 操作：新增
  - 目标：演示带记忆功能的多轮对话 RAG 系统

---

### 第九阶段：验证与测试

- [x] **9.1 安装项目依赖**
  - 操作：执行命令
  - 命令：`pip install -r requirements.txt`
  - 目标：确保所有依赖正确安装
  - ✅ 已完成：虚拟环境创建并安装所有依赖

- [x] **9.2 验证基础模块**
  - 操作：执行测试
  - 目标：确保各模块可正常导入和运行
  - ✅ 已完成：所有模块导入验证通过

---

## 项目最终结构

```
langchain/
├── README.md                         # 项目说明文档
├── requirements.txt                  # Python 依赖列表
├── .env.example                      # 环境变量模板
├── .gitignore                        # Git 忽略配置
├── data/                             # 测试数据目录
│   └── README.md                     # 数据目录说明
├── 01_loaders/                       # 文档加载器
│   └── pdf_loader.py
├── 02_splitters/                     # 文本分割器
│   └── text_splitter.py
├── 03_embeddings/                    # 向量嵌入
│   └── embeddings_demo.py
├── 04_vectorstores/                  # 向量存储
│   └── chroma_demo.py
├── 05_retrieval/                     # 检索策略
│   ├── similarity_search.py
│   ├── mmr_search.py
│   └── metadata_filter.py
├── 06_qa_chain/                      # 问答链
│   └── retrieval_qa.py
└── 07_conversational/                # 对话式RAG
    └── conversational_chain.py
```

---

## 学习路径建议

1. **Week 1**：完成第1-4阶段，理解文档处理和向量化基础
2. **Week 2**：完成第5-6阶段，掌握向量存储和检索策略
3. **Week 3**：完成第7-8阶段，构建完整的 RAG 问答系统

---

## 备注

- 所有代码均包含详细中文注释
- 每个模块可独立运行和学习
- 建议按顺序学习，循序渐进