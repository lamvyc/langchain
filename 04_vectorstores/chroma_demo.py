"""
04_vectorstores/chroma_demo.py
==============================
Chroma 向量数据库示例

本模块演示如何使用 Chroma 向量数据库存储和检索文档向量。
Chroma 是一个轻量级的本地向量数据库，非常适合学习和原型开发。

学习目标：
- 理解向量数据库的作用
- 掌握 Chroma 的基本操作
- 学会创建、查询和持久化向量库
"""

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# LangChain 组件
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


# 示例文档
SAMPLE_DOCUMENTS = [
    Document(
        page_content="LangChain 是一个用于构建大语言模型应用的开源框架。它提供了丰富的组件，包括提示模板、模型接口、向量存储等。",
        metadata={"source": "langchain_intro", "topic": "框架"}
    ),
    Document(
        page_content="RAG（检索增强生成）是一种结合检索和生成的技术。它首先从知识库中检索相关信息，然后将这些信息作为上下文提供给语言模型。",
        metadata={"source": "rag_intro", "topic": "技术"}
    ),
    Document(
        page_content="向量数据库是专门用于存储和检索向量的数据库。它支持高效的相似性搜索，是 RAG 系统的核心组件之一。",
        metadata={"source": "vectordb_intro", "topic": "数据库"}
    ),
    Document(
        page_content="Chroma 是一个开源的向量数据库，支持本地部署和云端服务。它易于使用，非常适合快速原型开发。",
        metadata={"source": "chroma_intro", "topic": "数据库"}
    ),
    Document(
        page_content="OpenAI 的 GPT 系列模型是目前最流行的大语言模型之一。GPT-4 在多项任务上展现出了接近人类的表现。",
        metadata={"source": "openai_intro", "topic": "模型"}
    ),
]


def check_api_key():
    """检查 API Key 配置"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-openai-api-key-here":
        print("⚠️  请先配置 OPENAI_API_KEY 环境变量")
        return False
    return True


def demo_create_vectorstore():
    """
    演示创建向量数据库
    """
    print("\n" + "=" * 60)
    print("1️⃣ 创建向量数据库")
    print("=" * 60)
    
    if not check_api_key():
        return None
    
    # 创建嵌入模型
    embeddings = OpenAIEmbeddings(model="BAAI/bge-large-zh-v1.5")
    
    print("\n📄 待存储的文档:")
    for i, doc in enumerate(SAMPLE_DOCUMENTS):
        print(f"   {i+1}. [{doc.metadata['topic']}] {doc.page_content[:40]}...")
    
    # 创建向量数据库（内存模式）
    vectordb = Chroma.from_documents(
        documents=SAMPLE_DOCUMENTS,
        embedding=embeddings,
    )
    
    print(f"\n✅ 向量数据库创建成功！")
    print(f"   文档数量: {vectordb._collection.count()}")
    
    return vectordb


def demo_similarity_search(vectordb):
    """
    演示相似度搜索
    """
    print("\n" + "=" * 60)
    print("2️⃣ 相似度搜索")
    print("=" * 60)
    
    if vectordb is None:
        print("⚠️  请先创建向量数据库")
        return
    
    # 查询
    query = "什么是 RAG 技术？"
    print(f"\n🔍 查询: {query}")
    
    # 执行搜索
    results = vectordb.similarity_search(query, k=3)
    
    print(f"\n📊 搜索结果（Top 3）:")
    print("-" * 50)
    
    for i, doc in enumerate(results):
        print(f"\n【结果 {i+1}】")
        print(f"   来源: {doc.metadata.get('source', 'unknown')}")
        print(f"   主题: {doc.metadata.get('topic', 'unknown')}")
        print(f"   内容: {doc.page_content[:100]}...")


def demo_similarity_search_with_score(vectordb):
    """
    演示带分数的相似度搜索
    """
    print("\n" + "=" * 60)
    print("3️⃣ 带分数的相似度搜索")
    print("=" * 60)
    
    if vectordb is None:
        print("⚠️  请先创建向量数据库")
        return
    
    query = "向量数据库有什么用？"
    print(f"\n🔍 查询: {query}")
    
    # 带分数的搜索
    results = vectordb.similarity_search_with_score(query, k=3)
    
    print(f"\n📊 搜索结果（含相似度分数）:")
    print("-" * 50)
    
    for i, (doc, score) in enumerate(results):
        print(f"\n【结果 {i+1}】分数: {score:.4f}")
        print(f"   来源: {doc.metadata.get('source', 'unknown')}")
        print(f"   内容: {doc.page_content[:80]}...")
    
    print("\n💡 说明: 分数越小表示越相似（L2距离）")


def demo_persist_vectorstore():
    """
    演示向量数据库持久化
    """
    print("\n" + "=" * 60)
    print("4️⃣ 向量数据库持久化")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    # 持久化目录
    persist_dir = Path(__file__).parent.parent / "chroma_db"
    
    # 清理旧数据
    if persist_dir.exists():
        shutil.rmtree(persist_dir)
    
    print(f"\n📁 持久化目录: {persist_dir}")
    
    # 创建嵌入模型
    embeddings = OpenAIEmbeddings(model="BAAI/bge-large-zh-v1.5")
    
    # 创建持久化向量数据库
    vectordb = Chroma.from_documents(
        documents=SAMPLE_DOCUMENTS,
        embedding=embeddings,
        persist_directory=str(persist_dir),
    )
    
    print(f"✅ 向量数据库已保存到磁盘")
    print(f"   文档数量: {vectordb._collection.count()}")
    
    # 演示重新加载
    print("\n🔄 重新加载向量数据库...")
    
    loaded_db = Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings,
    )
    
    print(f"✅ 加载成功！文档数量: {loaded_db._collection.count()}")
    
    # 测试查询
    query = "LangChain 是什么？"
    results = loaded_db.similarity_search(query, k=1)
    
    print(f"\n🔍 测试查询: {query}")
    print(f"   最佳匹配: {results[0].page_content[:60]}...")


def demo_add_documents(vectordb):
    """
    演示向现有数据库添加文档
    """
    print("\n" + "=" * 60)
    print("5️⃣ 添加新文档")
    print("=" * 60)
    
    if vectordb is None:
        print("⚠️  请先创建向量数据库")
        return vectordb
    
    # 新文档
    new_docs = [
        Document(
            page_content="深度学习是机器学习的一个分支，它使用多层神经网络来学习数据的表示。",
            metadata={"source": "deep_learning", "topic": "技术"}
        ),
        Document(
            page_content="Transformer 架构是现代大语言模型的基础，它引入了自注意力机制。",
            metadata={"source": "transformer", "topic": "架构"}
        ),
    ]
    
    print(f"\n?? 添加前文档数: {vectordb._collection.count()}")
    
    # 添加文档
    vectordb.add_documents(new_docs)
    
    print(f"📄 添加后文档数: {vectordb._collection.count()}")
    print("✅ 新文档添加成功！")
    
    return vectordb


def demo_with_pdf():
    """
    演示使用 PDF 文档创建向量库
    """
    print("\n" + "=" * 60)
    print("6️⃣ 从 PDF 创建向量数据库")
    print("=" * 60)
    
    # 查找 PDF 文件
    data_dir = Path(__file__).parent.parent / "data"
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("\n⚠️  data/ 目录下没有找到 PDF 文件")
        print("请将 PDF 文件放入 data/ 目录后再运行此示例")
        return
    
    if not check_api_key():
        return
    
    pdf_path = str(pdf_files[0])
    print(f"\n📁 加载文件: {pdf_path}")
    
    # 加载 PDF
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    print(f"   原始页数: {len(pages)}")
    
    # 分割文档
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(pages)
    print(f"   分割后块数: {len(chunks)}")
    
    # 创建向量数据库
    embeddings = OpenAIEmbeddings(model="BAAI/bge-large-zh-v1.5")
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
    )
    
    print(f"\n✅ 向量数据库创建成功！")
    print(f"   向量数量: {vectordb._collection.count()}")
    
    # 测试查询
    query = input("\n🔍 请输入查询内容（直接回车跳过）: ").strip()
    if query:
        results = vectordb.similarity_search(query, k=3)
        print(f"\n📊 搜索结果:")
        for i, doc in enumerate(results):
            print(f"\n【结果 {i+1}】")
            print(f"   {doc.page_content[:200]}...")


def main():
    """
    主函数：运行所有演示
    """
    print("=" * 60)
    print("💾 Chroma 向量数据库演示")
    print("=" * 60)
    
    print("""
💡 向量数据库的作用：

1. 存储：将文档的向量表示存入数据库
2. 索引：建立高效的检索索引
3. 查询：根据查询向量快速找到相似文档
4. 持久化：支持数据持久化到磁盘

Chroma 特点：
- 轻量级，易于安装和使用
- 支持内存和持久化两种模式
- 与 LangChain 无缝集成
    """)
    
    # 运行演示
    vectordb = demo_create_vectorstore()
    
    if vectordb:
        demo_similarity_search(vectordb)
        demo_similarity_search_with_score(vectordb)
        vectordb = demo_add_documents(vectordb)
    
    demo_persist_vectorstore()
    demo_with_pdf()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("""
📝 下一步：
- 学习不同的检索策略（MMR、元数据过滤等）
- 参见 05_retrieval/ 目录下的示例
    """)


if __name__ == "__main__":
    main()