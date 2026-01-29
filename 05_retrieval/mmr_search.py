"""
05_retrieval/mmr_search.py
==========================
最大边际相关（MMR）搜索示例

MMR（Maximum Marginal Relevance）是一种平衡相关性和多样性的检索策略。
它能避免返回过于相似的结果，提供更全面的信息覆盖。

学习目标：
- 理解 MMR 算法的原理
- 掌握 MMR 搜索的使用
- 对比 MMR 与普通相似度搜索的区别
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


# 准备示例文档（故意包含相似内容）
DOCUMENTS = [
    # 关于 Python 的多个相似文档
    Document(
        page_content="Python 是一种流行的编程语言，适合初学者学习。它的语法简洁清晰。",
        metadata={"topic": "Python", "aspect": "入门"}
    ),
    Document(
        page_content="Python 是一门易学的编程语言，新手友好。它有着清晰的语法规则。",
        metadata={"topic": "Python", "aspect": "入门"}
    ),
    Document(
        page_content="Python 在数据科学领域广泛应用，pandas 和 numpy 是常用库。",
        metadata={"topic": "Python", "aspect": "数据科学"}
    ),
    Document(
        page_content="Python 的机器学习生态非常丰富，scikit-learn 和 TensorFlow 很流行。",
        metadata={"topic": "Python", "aspect": "机器学习"}
    ),
    Document(
        page_content="Python 可以用于 Web 开发，Django 和 Flask 是主流框架。",
        metadata={"topic": "Python", "aspect": "Web开发"}
    ),
    # 其他主题
    Document(
        page_content="JavaScript 是前端开发的必备语言，React 和 Vue 是流行框架。",
        metadata={"topic": "JavaScript", "aspect": "前端"}
    ),
    Document(
        page_content="Rust 是一种注重安全和性能的系统编程语言，内存安全是其特色。",
        metadata={"topic": "Rust", "aspect": "系统编程"}
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


def demo_mmr_principle():
    """
    MMR 算法原理说明
    """
    print("\n" + "=" * 60)
    print("1️⃣ MMR 算法原理")
    print("=" * 60)
    
    print("""
📚 MMR（Maximum Marginal Relevance）算法：

目标：在保证相关性的同时，最大化结果的多样性

公式：
MMR = λ × Sim(query, doc) - (1-λ) × max(Sim(doc, selected_docs))

其中：
- λ (lambda)：相关性权重，范围 [0, 1]
- Sim(query, doc)：查询与候选文档的相似度
- max(Sim(doc, selected_docs))：候选文档与已选文档的最大相似度

执行过程：
┌─────────────────────────────────────────────────────────┐
│ 1. 使用查询向量检索 fetch_k 个最相似的文档               │
│                        ↓                                │
│ 2. 从候选集中选择与查询最相关的第一个文档                │
│                        ↓                                │
│ 3. 对剩余候选文档，计算 MMR 分数                        │
│    - 高相关性得分高                                     │
│    - 与已选文档相似则得分低                             │
│                        ↓                                │
│ 4. 选择 MMR 分数最高的文档                              │
│                        ↓                                │
│ 5. 重复步骤 3-4，直到选出 k 个文档                      │
└─────────────────────────────────────────────────────────┘

参数说明：
- fetch_k：初始检索的候选文档数（应 > k）
- k：最终返回的文档数
- lambda_mult：λ 值，越大越侧重相关性，越小越侧重多样性
    """)


def demo_compare_search():
    """
    对比普通搜索和 MMR 搜索
    """
    print("\n" + "=" * 60)
    print("2️⃣ 对比：普通搜索 vs MMR 搜索")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    query = "Python 编程语言"
    k = 4
    
    print(f"\n🔍 查询: {query}")
    print(f"📊 返回数量: {k}")
    
    # 普通相似度搜索
    print("\n" + "-" * 50)
    print("【普通相似度搜索】")
    print("-" * 50)
    
    results_sim = vectordb.similarity_search(query, k=k)
    
    for i, doc in enumerate(results_sim):
        print(f"   {i+1}. [{doc.metadata['aspect']}] {doc.page_content[:45]}...")
    
    # 统计主题分布
    aspects_sim = [doc.metadata['aspect'] for doc in results_sim]
    print(f"\n   📈 主题分布: {aspects_sim}")
    
    # MMR 搜索
    print("\n" + "-" * 50)
    print("【MMR 搜索】")
    print("-" * 50)
    
    results_mmr = vectordb.max_marginal_relevance_search(
        query, 
        k=k,
        fetch_k=7,  # 初始检索更多候选
    )
    
    for i, doc in enumerate(results_mmr):
        print(f"   {i+1}. [{doc.metadata['aspect']}] {doc.page_content[:45]}...")
    
    # 统计主题分布
    aspects_mmr = [doc.metadata['aspect'] for doc in results_mmr]
    print(f"\n   📈 主题分布: {aspects_mmr}")
    
    print("""
💡 观察：
- 普通搜索：返回的结果可能主题重复
- MMR 搜索：结果覆盖更多不同的主题/方面
    """)


def demo_mmr_lambda():
    """
    演示 lambda 参数的影响
    """
    print("\n" + "=" * 60)
    print("3️⃣ Lambda 参数的影响")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    query = "学习 Python 编程"
    k = 3
    
    print(f"\n🔍 查询: {query}")
    
    # 不同的 lambda 值
    lambda_values = [0.0, 0.5, 1.0]
    
    for lambda_val in lambda_values:
        print(f"\n" + "-" * 50)
        print(f"【lambda = {lambda_val}】", end="")
        
        if lambda_val == 0.0:
            print("（最大多样性）")
        elif lambda_val == 1.0:
            print("（最大相关性，等同于普通搜索）")
        else:
            print("（平衡模式）")
        
        print("-" * 50)
        
        results = vectordb.max_marginal_relevance_search(
            query,
            k=k,
            fetch_k=7,
            lambda_mult=lambda_val,
        )
        
        for i, doc in enumerate(results):
            print(f"   {i+1}. [{doc.metadata['aspect']}] {doc.page_content[:40]}...")


def demo_mmr_fetch_k():
    """
    演示 fetch_k 参数的影响
    """
    print("\n" + "=" * 60)
    print("4️⃣ Fetch_k 参数的影响")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    query = "Python"
    k = 3
    
    print(f"\n🔍 查询: {query}")
    print(f"📊 返回数量 k = {k}")
    
    # 不同的 fetch_k 值
    fetch_k_values = [3, 5, 7]
    
    for fetch_k in fetch_k_values:
        print(f"\n" + "-" * 50)
        print(f"【fetch_k = {fetch_k}】候选池大小")
        print("-" * 50)
        
        results = vectordb.max_marginal_relevance_search(
            query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=0.5,
        )
        
        aspects = []
        for i, doc in enumerate(results):
            aspects.append(doc.metadata['aspect'])
            print(f"   {i+1}. [{doc.metadata['aspect']}] {doc.page_content[:40]}...")
        
        unique_aspects = len(set(aspects))
        print(f"   → 唯一主题数: {unique_aspects}/{len(aspects)}")
    
    print("""
💡 说明：
- fetch_k 越大，候选池越大，多样性潜力越高
- fetch_k 应该 >= k，建议设置为 k 的 2-3 倍
    """)


def demo_mmr_retriever():
    """
    使用 Retriever 接口配置 MMR
    """
    print("\n" + "=" * 60)
    print("5️⃣ 使用 Retriever 接口")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    # 创建 MMR Retriever
    mmr_retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 4,
            "fetch_k": 7,
            "lambda_mult": 0.5,
        }
    )
    
    query = "Python 应用场景"
    print(f"\n🔍 查询: {query}")
    
    # 使用 retriever
    docs = mmr_retriever.invoke(query)
    
    print("\n📊 MMR Retriever 结果:")
    for i, doc in enumerate(docs):
        print(f"   {i+1}. [{doc.metadata['aspect']}] {doc.page_content[:45]}...")
    
    print("""
💡 配置说明:
retriever = vectordb.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 4,           # 返回文档数
        "fetch_k": 7,     # 候选池大小
        "lambda_mult": 0.5  # 多样性权重
    }
)
    """)


def main():
    """主函数"""
    print("=" * 60)
    print("🎯 MMR（最大边际相关）搜索演示")
    print("=" * 60)
    
    print("""
💡 为什么需要 MMR？

普通相似度搜索的问题：
- 返回的文档可能高度相似/重复
- 信息覆盖面窄
- 可能错过重要的相关信息

MMR 的优势：
✅ 平衡相关性和多样性
✅ 减少冗余信息
✅ 提供更全面的上下文
    """)
    
    # 运行演示
    demo_mmr_principle()
    demo_compare_search()
    demo_mmr_lambda()
    demo_mmr_fetch_k()
    demo_mmr_retriever()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("""
?? 最佳实践：
1. k=4~6, fetch_k=k*2~3
2. lambda_mult=0.5~0.7 适合大多数场景
3. 结果需要高多样性时降低 lambda

下一步：
- 学习元数据过滤
- 参见 05_retrieval/metadata_filter.py
    """)


if __name__ == "__main__":
    main()