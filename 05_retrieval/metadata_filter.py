"""
05_retrieval/metadata_filter.py
===============================
元数据过滤示例

本模块演示如何使用元数据（Metadata）进行精确过滤，
实现更精准的检索结果。

学习目标：
- 理解元数据在 RAG 中的作用
- 掌握基于元数据的过滤方法
- 学会组合使用相似度搜索和元数据过滤
"""

import os
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


# 准备带丰富元数据的示例文档
DOCUMENTS = [
    # Python 相关
    Document(
        page_content="Python 基础语法入门：变量、数据类型、条件语句和循环。",
        metadata={
            "category": "编程",
            "language": "Python",
            "level": "beginner",
            "year": 2024,
            "author": "张三"
        }
    ),
    Document(
        page_content="Python 高级特性：装饰器、生成器、上下文管理器详解。",
        metadata={
            "category": "编程",
            "language": "Python",
            "level": "advanced",
            "year": 2024,
            "author": "李四"
        }
    ),
    Document(
        page_content="Python 数据分析：使用 pandas 进行数据清洗和处理。",
        metadata={
            "category": "数据科学",
            "language": "Python",
            "level": "intermediate",
            "year": 2023,
            "author": "王五"
        }
    ),
    # JavaScript 相关
    Document(
        page_content="JavaScript ES6+ 新特性：箭头函数、解构赋值、Promise。",
        metadata={
            "category": "编程",
            "language": "JavaScript",
            "level": "intermediate",
            "year": 2024,
            "author": "张三"
        }
    ),
    Document(
        page_content="React Hooks 实战：useState、useEffect、自定义 Hook。",
        metadata={
            "category": "前端",
            "language": "JavaScript",
            "level": "intermediate",
            "year": 2024,
            "author": "赵六"
        }
    ),
    # 机器学习相关
    Document(
        page_content="机器学习入门：监督学习与非监督学习的区别和应用场景。",
        metadata={
            "category": "AI",
            "language": "Python",
            "level": "beginner",
            "year": 2023,
            "author": "李四"
        }
    ),
    Document(
        page_content="深度学习实战：使用 PyTorch 构建神经网络模型。",
        metadata={
            "category": "AI",
            "language": "Python",
            "level": "advanced",
            "year": 2024,
            "author": "王五"
        }
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


def demo_metadata_overview():
    """
    元数据概述
    """
    print("\n" + "=" * 60)
    print("1️⃣ 元数据概述")
    print("=" * 60)
    
    print("""
📚 什么是元数据（Metadata）？

元数据是描述文档属性的附加信息，例如：
- 来源（source）
- 作者（author）
- 日期（date）
- 类别（category）
- 页码（page）
- 自定义标签

元数据的作用：
✅ 精确过滤：按条件筛选文档
✅ 结果排序：按时间、优先级排序
✅ 权限控制：按用户权限过滤
✅ 追溯来源：知道答案从哪来
    """)
    
    print("\n📄 示例文档的元数据字段：")
    print("-" * 40)
    
    sample_doc = DOCUMENTS[0]
    for key, value in sample_doc.metadata.items():
        print(f"   {key}: {value}")


def demo_basic_filter():
    """
    基础元数据过滤
    """
    print("\n" + "=" * 60)
    print("2️⃣ 基础元数据过滤")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    query = "编程入门"
    
    # 不带过滤的搜索
    print(f"\n🔍 查询: {query}")
    print("\n【不带过滤】")
    print("-" * 40)
    
    results = vectordb.similarity_search(query, k=3)
    for i, doc in enumerate(results):
        print(f"   {i+1}. [{doc.metadata['language']}] {doc.page_content[:40]}...")
    
    # 带过滤的搜索：只要 Python
    print("\n【过滤: language = Python】")
    print("-" * 40)
    
    results_filtered = vectordb.similarity_search(
        query,
        k=3,
        filter={"language": "Python"}
    )
    for i, doc in enumerate(results_filtered):
        print(f"   {i+1}. [{doc.metadata['language']}] {doc.page_content[:40]}...")


def demo_complex_filter():
    """
    复杂过滤条件
    """
    print("\n" + "=" * 60)
    print("3️⃣ 复杂过滤条件")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    query = "Python 学习"
    
    # 组合过滤条件
    print(f"\n🔍 查询: {query}")
    
    # 条件1：Python + 初级
    print("\n【过滤: Python AND beginner】")
    print("-" * 40)
    
    results = vectordb.similarity_search(
        query,
        k=3,
        filter={
            "$and": [
                {"language": "Python"},
                {"level": "beginner"}
            ]
        }
    )
    for i, doc in enumerate(results):
        print(f"   {i+1}. [{doc.metadata['level']}] {doc.page_content[:40]}...")
    
    # 条件2：Python OR JavaScript
    print("\n【过滤: Python OR JavaScript】")
    print("-" * 40)
    
    results = vectordb.similarity_search(
        query,
        k=4,
        filter={
            "$or": [
                {"language": "Python"},
                {"language": "JavaScript"}
            ]
        }
    )
    for i, doc in enumerate(results):
        print(f"   {i+1}. [{doc.metadata['language']}] {doc.page_content[:35]}...")


def demo_comparison_filter():
    """
    比较运算符过滤
    """
    print("\n" + "=" * 60)
    print("4️⃣ 比较运算符过滤")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    query = "编程技术"
    
    print(f"\n🔍 查询: {query}")
    
    # 2024年的文档
    print("\n【过滤: year = 2024】")
    print("-" * 40)
    
    results = vectordb.similarity_search(
        query,
        k=5,
        filter={"year": 2024}
    )
    for i, doc in enumerate(results):
        print(f"   {i+1}. [{doc.metadata['year']}] {doc.page_content[:40]}...")
    
    # 2023年及之后的文档（使用 $gte）
    print("\n【过滤: year >= 2023】")
    print("-" * 40)
    
    results = vectordb.similarity_search(
        query,
        k=5,
        filter={"year": {"$gte": 2023}}
    )
    for i, doc in enumerate(results):
        print(f"   {i+1}. [{doc.metadata['year']}] {doc.page_content[:40]}...")
    
    print("""
📚 Chroma 支持的比较运算符：
- $eq: 等于（默认）
- $ne: 不等于
- $gt: 大于
- $gte: 大于等于
- $lt: 小于
- $lte: 小于等于
- $in: 在列表中
- $nin: 不在列表中
    """)


def demo_in_filter():
    """
    IN 运算符过滤
    """
    print("\n" + "=" * 60)
    print("5️⃣ IN 运算符过滤")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    query = "技术文章"
    
    print(f"\n🔍 查询: {query}")
    
    # 特定作者的文档
    print("\n【过滤: author IN ['张三', '李四']】")
    print("-" * 40)
    
    results = vectordb.similarity_search(
        query,
        k=5,
        filter={"author": {"$in": ["张三", "李四"]}}
    )
    for i, doc in enumerate(results):
        print(f"   {i+1}. [{doc.metadata['author']}] {doc.page_content[:40]}...")
    
    # 排除特定级别
    print("\n【过滤: level NOT IN ['beginner']】")
    print("-" * 40)
    
    results = vectordb.similarity_search(
        query,
        k=5,
        filter={"level": {"$nin": ["beginner"]}}
    )
    for i, doc in enumerate(results):
        print(f"   {i+1}. [{doc.metadata['level']}] {doc.page_content[:40]}...")


def demo_retriever_with_filter():
    """
    在 Retriever 中使用过滤
    """
    print("\n" + "=" * 60)
    print("6️⃣ Retriever 中使用过滤")
    print("=" * 60)
    
    vectordb = create_vectorstore()
    if not vectordb:
        return
    
    # 创建带过滤的 Retriever
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 3,
            "filter": {"category": "AI"}
        }
    )
    
    query = "学习人工智能"
    print(f"\n🔍 查询: {query}")
    print("📌 过滤条件: category = AI")
    print("-" * 40)
    
    docs = retriever.invoke(query)
    
    for i, doc in enumerate(docs):
        print(f"   {i+1}. [{doc.metadata['category']}] {doc.page_content[:40]}...")
    
    print("""
💡 在 Chain 中使用带过滤的 Retriever：

retriever = vectordb.as_retriever(
    search_kwargs={
        "k": 5,
        "filter": {"category": "技术"}
    }
)

chain = RetrievalQA.from_chain_type(
    llm=chat,
    retriever=retriever
)
    """)


def demo_filter_best_practices():
    """
    最佳实践
    """
    print("\n" + "=" * 60)
    print("7️⃣ 元数据过滤最佳实践")
    print("=" * 60)
    
    print("""
📝 设计元数据的建议：

1. 【必要字段】
   - source: 文档来源（文件名、URL）
   - page: 页码或章节
   - timestamp: 创建/更新时间

2. 【业务字段】
   - category: 文档类别
   - author: 作者
   - department: 部门
   - access_level: 访问级别

3. 【注意事项】
   ⚠️ 元数据值应该是简单类型（字符串、数字、布尔）
   ⚠️ 避免在元数据中存储大量文本
   ⚠️ 考虑查询性能，不要过度细分

4. 【常见过滤场景】
   - 按时间范围过滤（最近一周/一月的文档）
   - 按部门/权限过滤（只查询本部门的知识）
   - 按文档类型过滤（只查政策类文档）
   - 按来源过滤（只查官方文档）

5. 【动态过滤】
   可以根据用户输入动态构建过滤条件：
   
   def get_filter(user_role, time_range):
       filter_dict = {}
       if user_role != "admin":
           filter_dict["access_level"] = "public"
       if time_range:
           filter_dict["year"] = {"$gte": 2023}
       return filter_dict
    """)


def main():
    """主函数"""
    print("=" * 60)
    print("🏷️ 元数据过滤演示")
    print("=" * 60)
    
    print("""
💡 为什么需要元数据过滤？

仅靠语义相似度搜索可能不够精确：
- 用户可能只想要特定时间范围的内容
- 需要按权限/部门过滤敏感信息
- 需要限定文档类型或来源

元数据过滤 + 语义搜索 = 更精准的 RAG
    """)
    
    # 运行演示
    demo_metadata_overview()
    demo_basic_filter()
    demo_complex_filter()
    demo_comparison_filter()
    demo_in_filter()
    demo_retriever_with_filter()
    demo_filter_best_practices()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("""
📝 检索策略总结：

1. similarity_search: 基础相似度搜索
2. MMR: 平衡相关性与多样性
3. 元数据过滤: 精确条件筛选

三者可以组合使用，实现最优检索效果！

下一步：
- 学习构建完整的问答链
- 参见 06_qa_chain/retrieval_qa.py
    """)


if __name__ == "__main__":
    main()