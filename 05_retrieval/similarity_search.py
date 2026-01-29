"""
05_retrieval/similarity_search.py
=================================
相似度搜索示例

本模块演示基础的相似度搜索方法，这是 RAG 系统中最常用的检索方式。

学习目标：
- 理解相似度搜索的原理
- 掌握不同的相似度度量方法
- 学会调整搜索参数
"""

import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


# 准备示例文档
DOCUMENTS = [
    Document(
        page_content="Python 是一种高级编程语言，以其简洁的语法和强大的库生态而闻名。它广泛应用于数据科学、机器学习和Web开发。",
        metadata={"category": "编程语言", "difficulty": "初级"}
    ),
    Document(
        page_content="JavaScript 是Web开发的核心语言，它可以在浏览器中运行，也可以通过Node.js在服务器端运行。",
        metadata={"category": "编程语言", "difficulty": "初级"}
    ),
    Document(
        page_content="机器学习是人工智能的一个分支，它使计算机能够从数据中学习模式，而无需明确编程。",
        metadata={"category": "AI", "difficulty": "中级"}
    ),
    Document(
        page_content="深度学习使用多层神经网络来学习数据的复杂表示。它在图像识别、语音识别等领域取得了巨大成功。",
        metadata={"category": "AI", "difficulty": "高级"}
    ),
    Document(
        page_content="自然语言处理（NLP）是AI的一个分支，专注于使计算机理解和生成人类语言。",
        metadata={"category": "AI", "difficulty": "中级"}
    ),
    Document(
        page_content="RAG（检索增强生成）结合了信息检索和文本生成技术，能够基于外部知识库生成准确的回答。",
        metadata={"category": "AI", "difficulty": "高级"}
    ),
    Document(
        page_content="Docker 是一个容器化平台，它可以将应用程序及其依赖打包成容器，实现"一次构建，到处运行"。",
        metadata={"category": "DevOps", "difficulty": "中级"}
    ),
    Document(
        page_content="Kubernetes 是一个容器编排平台，用于自动化部署、扩展和管理容器化应用程序。",
        metadata={"category": "DevOps", "difficulty": "高级"}
    ),
]


def check_api_key():
    """检查 API Key"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-openai-api-key-here":
        print("⚠️  请先配置 OPENAI_API_KEY 环境变量")
        return False
    return True


def create_vectorstore():
    """创建向量数据库"""
    if not check_api_key():
        return None
    
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(
        documents=DOCUMENTS,
        embedding=embeddings,
    )
    return vectordb


def demo_basic_search():
    """
    基础相似度搜索
    """
    print("\n" + "=" * 60)
    print("1️⃣ 基础相似度搜索")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    # 查询
    queries = [
        "如何学习编程？",
        "什么是深度学习？",
        "容器技术有哪些？",
    ]
    
    for query in queries:
        print(f"\n🔍 查询: {query}")
        print("-" * 40)
        
        # 搜索 top 2 结果
        results = vectordb.similarity_search(query, k=2)
        
        for i, doc in enumerate(results):
            print(f"   {i+1}. [{doc.metadata['category']}] {doc.page_content[:50]}...")


def demo_search_with_score():
    """
    带分数的相似度搜索
    """
    print("\n" + "=" * 60)
    print("2️⃣ 带分数的相似度搜索")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    query = "人工智能和机器学习的关系"
    print(f"\n🔍 查询: {query}")
    print("-" * 40)
    
    # 带分数的搜索
    results = vectordb.similarity_search_with_score(query, k=4)
    
    print("\n📊 结果（按相似度排序）:")
    for i, (doc, score) in enumerate(results):
        # 分数越小越相似（L2距离）
        bar_length = max(1, int((2 - score) * 10))
        bar = "█" * bar_length
        print(f"\n   {i+1}. 距离: {score:.4f} {bar}")
        print(f"      类别: {doc.metadata['category']}")
        print(f"      内容: {doc.page_content[:60]}...")


def demo_search_with_threshold():
    """
    带阈值过滤的搜索
    """
    print("\n" + "=" * 60)
    print("3️⃣ 带阈值过滤的搜索")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    query = "Python编程入门"
    threshold = 1.0  # 距离阈值
    
    print(f"\n🔍 查询: {query}")
    print(f"📏 距离阈值: {threshold}")
    print("-" * 40)
    
    # 获取带分数的结果
    results = vectordb.similarity_search_with_score(query, k=5)
    
    # 过滤低于阈值的结果
    filtered_results = [(doc, score) for doc, score in results if score < threshold]
    
    print(f"\n📊 过滤前: {len(results)} 个结果")
    print(f"📊 过滤后: {len(filtered_results)} 个结果")
    
    print("\n✅ 符合阈值的结果:")
    for i, (doc, score) in enumerate(filtered_results):
        print(f"   {i+1}. [{score:.4f}] {doc.page_content[:50]}...")
    
    if len(filtered_results) < len(results):
        print("\n❌ 被过滤的结果:")
        for doc, score in results:
            if score >= threshold:
                print(f"   [{score:.4f}] {doc.page_content[:50]}...")


def demo_retriever_interface():
    """
    使用 Retriever 接口
    """
    print("\n" + "=" * 60)
    print("4️⃣ 使用 Retriever 接口")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    # 将向量库转换为 Retriever
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    query = "容器化部署方案"
    print(f"\n🔍 查询: {query}")
    print("-" * 40)
    
    # 使用 retriever 检索
    docs = retriever.invoke(query)
    
    print(f"\n📊 检索到 {len(docs)} 个文档:")
    for i, doc in enumerate(docs):
        print(f"   {i+1}. [{doc.metadata['category']}] {doc.page_content[:50]}...")
    
    print("""
💡 Retriever 接口的优势：
- 统一的调用接口
- 可以无缝集成到 Chain 和 Agent 中
- 支持多种搜索类型配置
    """)


def demo_similarity_metrics():
    """
    相似度度量方法说明
    """
    print("\n" + "=" * 60)
    print("5️⃣ 相似度度量方法")
    print("=" * 60)
    
    print("""
📚 常用的向量相似度度量方法：

┌──────────────────┬─────────────────────────────────────┐
│ 方法             │ 说明                                │
├──────────────────┼─────────────────────────────────────┤
│ 余弦相似度       │ 测量向量夹角，范围 [-1, 1]          │
│ (Cosine)         │ 值越大越相似                        │
├──────────────────┼─────────────────────────────────────┤
│ 欧氏距离         │ 测量向量间的直线距离                │
│ (L2/Euclidean)   │ 值越小越相似（Chroma 默认）         │
├──────────────────┼─────────────────────────────────────┤
│ 点积             │ 向量的内积                          │
│ (Dot Product)    │ 值越大越相似（需归一化向量）        │
└──────────────────┴─────────────────────────────────────┘

💡 选择建议：
- 文本语义相似度：余弦相似度（不受文本长度影响）
- 通用场景：欧氏距离
- 高性能需求：点积（计算最快）
    """)


def main():
    """主函数"""
    print("=" * 60)
    print("?? 相似度搜索演示")
    print("=" * 60)
    
    print("""
?? 相似度搜索原理：

1. 将查询文本转换为向量
2. 计算查询向量与所有文档向量的距离/相似度
3. 返回最相似的 k 个文档

特点：
✅ 简单直接
✅ 计算效率高
⚠️  可能返回相似但重复的内容
    """)
    
    # 运行演示
    demo_similarity_metrics()
    demo_basic_search()
    demo_search_with_score()
    demo_search_with_threshold()
    demo_retriever_interface()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("""
📝 下一步：
- 学习 MMR 搜索（平衡相关性与多样性）
- 参见 05_retrieval/mmr_search.py
    """)


if __name__ == "__main__":
    main()