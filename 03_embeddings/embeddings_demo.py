"""
03_embeddings/embeddings_demo.py
================================
向量嵌入（Embeddings）示例

本模块演示如何使用 OpenAI Embeddings 将文本转换为向量，
这是 RAG 系统的核心步骤之一。

学习目标：
- 理解什么是文本嵌入（Embedding）
- 掌握 OpenAI Embeddings 的使用
- 理解向量相似度的概念
- 学会计算文本之间的相似度
"""

import os
from dotenv import load_dotenv
load_dotenv()

# LangChain OpenAI Embeddings
from langchain_openai import OpenAIEmbeddings


def create_embeddings():
    """
    创建 OpenAI Embeddings 实例
    """
    # 检查 API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "sk-your-openai-api-key-here":
        print("⚠️  请先配置 OPENAI_API_KEY 环境变量")
        print("   1. 复制 .env.example 为 .env")
        print("   2. 填入你的 OpenAI API Key")
        return None
    
    # 创建 Embeddings 实例
    embeddings = OpenAIEmbeddings(
        model="text-embedding-ada-002",  # OpenAI 推荐的嵌入模型
        # 或使用最新的 text-embedding-3-small / text-embedding-3-large
    )
    
    return embeddings


def demo_single_embedding():
    """
    演示单个文本的嵌入
    """
    print("\n" + "=" * 60)
    print("1️⃣ 单个文本嵌入示例")
    print("=" * 60)
    
    embeddings = create_embeddings()
    if not embeddings:
        return
    
    # 单个文本
    text = "LangChain 是一个用于构建 LLM 应用的框架"
    
    print(f"\n📝 原始文本: {text}")
    
    # 生成嵌入向量
    vector = embeddings.embed_query(text)
    
    print(f"\n📊 嵌入结果:")
    print(f"   向量维度: {len(vector)}")
    print(f"   前5个值: {vector[:5]}")
    print(f"   后5个值: {vector[-5:]}")


def demo_batch_embedding():
    """
    演示批量文本嵌入
    """
    print("\n" + "=" * 60)
    print("2️⃣ 批量文本嵌入示例")
    print("=" * 60)
    
    embeddings = create_embeddings()
    if not embeddings:
        return
    
    # 多个文本
    texts = [
        "人工智能正在改变世界",
        "机器学习是AI的重要分支",
        "深度学习使用神经网络",
        "今天天气真好",
    ]
    
    print("\n📝 原始文本列表:")
    for i, text in enumerate(texts):
        print(f"   {i+1}. {text}")
    
    # 批量生成嵌入向量
    vectors = embeddings.embed_documents(texts)
    
    print(f"\n📊 嵌入结果:")
    print(f"   文本数量: {len(vectors)}")
    print(f"   每个向量维度: {len(vectors[0])}")


def demo_similarity():
    """
    演示向量相似度计算
    """
    print("\n" + "=" * 60)
    print("3️⃣ 向量相似度计算示例")
    print("=" * 60)
    
    embeddings = create_embeddings()
    if not embeddings:
        return
    
    # 准备文本
    query = "什么是机器学习？"
    documents = [
        "机器学习是人工智能的一个分支，它使计算机能够从数据中学习",
        "深度学习是机器学习的子集，使用多层神经网络",
        "今天的天气非常晴朗，适合户外运动",
        "Python 是一种流行的编程语言",
    ]
    
    print(f"\n🔍 查询: {query}")
    print("\n?? 待比较的文档:")
    for i, doc in enumerate(documents):
        print(f"   {i+1}. {doc}")
    
    # 生成向量
    query_vector = embeddings.embed_query(query)
    doc_vectors = embeddings.embed_documents(documents)
    
    # 计算余弦相似度
    def cosine_similarity(vec1, vec2):
        """计算两个向量的余弦相似度"""
        import math
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        return dot_product / (norm1 * norm2)
    
    print("\n📊 相似度结果:")
    print("-" * 50)
    
    similarities = []
    for i, doc_vec in enumerate(doc_vectors):
        sim = cosine_similarity(query_vector, doc_vec)
        similarities.append((i, sim, documents[i]))
    
    # 按相似度排序
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    for rank, (idx, sim, doc) in enumerate(similarities, 1):
        bar = "█" * int(sim * 20)
        print(f"   {rank}. [{sim:.4f}] {bar}")
        print(f"      {doc[:50]}...")
    
    print("\n💡 说明: 相似度越接近 1，表示语义越相近")


def demo_embedding_models():
    """
    介绍不同的嵌入模型
    """
    print("\n" + "=" * 60)
    print("4️⃣ OpenAI 嵌入模型介绍")
    print("=" * 60)
    
    print("""
📚 OpenAI 提供的嵌入模型:

┌─────────────────────────────┬──────────┬─────────────┐
│ 模型                         │ 维度     │ 特点        │
├─────────────────────────────┼──────────┼─────────────┤
│ text-embedding-ada-002      │ 1536     │ 经典模型    │
│ text-embedding-3-small      │ 1536     │ 更快更便宜  │
│ text-embedding-3-large      │ 3072     │ 更高精度    │
└─────────────────────────────┴──────────┴─────────────┘

💡 选择建议:
- 一般场景: text-embedding-3-small（性价比最高）
- 高精度需求: text-embedding-3-large
- 兼容旧系统: text-embedding-ada-002
    """)


def main():
    """
    主函数：运行所有演示
    """
    print("=" * 60)
    print("🔢 向量嵌入（Embeddings）演示")
    print("=" * 60)
    
    print("""
💡 什么是文本嵌入？

文本嵌入是将文本转换为数值向量的过程。
这些向量捕获了文本的语义信息，使得：
- 语义相似的文本，向量也相近
- 可以用数学方法计算文本相似度
- 支持高效的向量检索

在 RAG 中的作用：
1. 将文档块转换为向量存入向量库
2. 将用户查询转换为向量
3. 通过向量相似度找到相关文档
    """)
    
    # 运行各个演示
    demo_embedding_models()
    demo_single_embedding()
    demo_batch_embedding()
    demo_similarity()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("""
📝 下一步：
- 学习如何将嵌入向量存入向量数据库
- 参见 04_vectorstores/chroma_demo.py
    """)


if __name__ == "__main__":
    main()