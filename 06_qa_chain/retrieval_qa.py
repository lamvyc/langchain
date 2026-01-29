"""
06_qa_chain/retrieval_qa.py
===========================
RAG 问答链示例（使用 LCEL）

本模块演示如何构建完整的 RAG 问答流程，
将检索和生成结合起来，实现基于知识库的智能问答。

学习目标：
- 理解 RAG 问答的完整流程
- 掌握使用 LCEL（LangChain Expression Language）构建 RAG 链
- 学会自定义提示模板
"""

import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# LangChain 组件
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.documents import Document


# 准备知识库文档
KNOWLEDGE_BASE = [
    Document(
        page_content="""
LangChain 是一个用于构建大语言模型(LLM)应用的开源框架。
它提供了丰富的组件和工具，帮助开发者快速构建 AI 应用。
主要特点包括：
1. 模块化设计，组件可复用
2. 支持多种 LLM 提供商（OpenAI、Anthropic 等）
3. 内置向量存储和检索功能
4. 提供 Chain 和 Agent 抽象
""",
        metadata={"source": "langchain_overview", "topic": "框架介绍"}
    ),
    Document(
        page_content="""
RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合检索和生成的技术。
工作流程：
1. 将知识库文档分块并向量化
2. 用户提问时，检索相关文档片段
3. 将检索结果作为上下文，与问题一起发送给 LLM
4. LLM 基于上下文生成准确的回答

优势：
- 减少 LLM 幻觉
- 支持实时更新知识
- 可追溯答案来源
""",
        metadata={"source": "rag_introduction", "topic": "技术原理"}
    ),
    Document(
        page_content="""
向量数据库是 RAG 系统的核心组件之一。
常用的向量数据库包括：
1. Chroma - 轻量级，适合原型开发
2. FAISS - Facebook 开源，高性能
3. Pinecone - 云端托管服务
4. Milvus - 企业级开源方案
5. Weaviate - 支持混合搜索

选择建议：
- 学习阶段：Chroma
- 生产环境：根据规模选择 FAISS 或云服务
""",
        metadata={"source": "vectordb_comparison", "topic": "技术选型"}
    ),
    Document(
        page_content="""
Embedding（嵌入）是将文本转换为向量的过程。
常用的嵌入模型：
1. OpenAI text-embedding-ada-002（1536维）
2. OpenAI text-embedding-3-small（1536维，更快更便宜）
3. OpenAI text-embedding-3-large（3072维，更高精度）
4. Sentence-BERT（开源，可本地部署）
5. BGE（智源开源，中文效果好）

嵌入模型的选择会影响检索效果。
""",
        metadata={"source": "embedding_models", "topic": "技术选型"}
    ),
    Document(
        page_content="""
文本分割是 RAG 预处理的重要步骤。
分割策略：
1. 按字符数分割（CharacterTextSplitter）
2. 递归分割（RecursiveCharacterTextSplitter）- 推荐
3. 按语义分割（基于模型）
4. 按文档结构分割（Markdown、HTML 等）

参数建议：
- chunk_size: 500-1500 字符
- chunk_overlap: chunk_size 的 10-20%
""",
        metadata={"source": "text_splitting", "topic": "数据处理"}
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
    embeddings = OpenAIEmbeddings(model="BAAI/bge-large-zh-v1.5")
    vectordb = Chroma.from_documents(
        documents=KNOWLEDGE_BASE,
        embedding=embeddings,
    )
    return vectordb


def format_docs(docs):
    """格式化文档列表为字符串"""
    return "\n\n".join(doc.page_content for doc in docs)


def demo_rag_flow():
    """
    演示 RAG 完整流程
    """
    print("\n" + "=" * 60)
    print("1️⃣ RAG 完整流程演示")
    print("=" * 60)
    
    print("""
📊 RAG 流程图：

┌─────────────┐
│  用户提问    │
└──────┬──────┘
       ↓
┌─────────────┐     ┌─────────────┐
│  向量化查询  │ --> │  向量数据库  │
└──────┬──────┘     └──────┬──────┘
       ↓                   ↓
       └─────────┬─────────┘
                 ↓
       ┌─────────────────┐
       │  检索相关文档    │
       └────────┬────────┘
                ↓
       ┌─────────────────┐
       │  构建提示模板    │
       │  (上下文+问题)   │
       └────────┬────────┘
                ↓
       ┌─────────────────┐
       │    LLM 生成     │
       └────────┬────────┘
                ↓
       ┌─────────────────┐
       │    返回答案     │
       └─────────────────┘
    """)


def demo_basic_rag():
    """
    基础 RAG 链（使用 LCEL）
    """
    print("\n" + "=" * 60)
    print("2️⃣ 基础 RAG 链（LCEL 方式）")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    # 创建组件
    vectordb = create_vectorstore()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    
    # 创建提示模板
    template = """根据以下上下文回答问题。如果上下文中没有相关信息，请说"我不知道"。

上下文：
{context}

问题：{question}

回答："""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # 使用 LCEL 构建 RAG 链
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # 测试问答
    questions = [
        "什么是 LangChain？",
        "RAG 有什么优势？",
        "如何选择向量数据库？",
    ]
    
    for q in questions:
        print(f"\n❓ 问题: {q}")
        print("-" * 40)
        
        answer = rag_chain.invoke(q)
        print(f"💬 回答: {answer[:200]}...")


def demo_rag_with_sources():
    """
    返回引用来源的 RAG 链
    """
    print("\n" + "=" * 60)
    print("3️⃣ 返回引用来源")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    vectordb = create_vectorstore()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    retriever = vectordb.as_retriever(search_kwargs={"k": 2})
    
    template = """根据以下上下文回答问题：

上下文：
{context}

问题：{question}

回答："""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # 构建返回来源的链
    def create_rag_chain_with_sources():
        def get_context_and_question(input_dict):
            question = input_dict["question"]
            docs = retriever.invoke(question)
            return {
                "context": format_docs(docs),
                "question": question,
                "source_documents": docs
            }
        
        return get_context_and_question
    
    # 手动执行以获取来源
    question = "文本分割有哪些策略？"
    print(f"\n❓ 问题: {question}")
    print("-" * 40)
    
    # 检索文档
    docs = retriever.invoke(question)
    context = format_docs(docs)
    
    # 生成答案
    answer = (prompt | llm | StrOutputParser()).invoke({
        "context": context,
        "question": question
    })
    
    print(f"💬 回答:\n{answer}")
    
    print("\n📚 引用来源:")
    for i, doc in enumerate(docs):
        print(f"\n   【来源 {i+1}】")
        print(f"   source: {doc.metadata.get('source', 'unknown')}")
        print(f"   topic: {doc.metadata.get('topic', 'unknown')}")
        print(f"   内容: {doc.page_content[:80]}...")


def demo_custom_prompt():
    """
    自定义提示模板
    """
    print("\n" + "=" * 60)
    print("4️⃣ 自定义提示模板")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    vectordb = create_vectorstore()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    
    # 自定义专业提示模板
    template = """你是一个专业的技术助手，请根据以下上下文信息回答用户的问题。

上下文信息：
{context}

用户问题：{question}

回答要求：
1. 只根据上下文信息回答，不要编造
2. 如果上下文中没有相关信息，请明确说明
3. 回答要简洁明了，使用中文
4. 如果适用，使用列表或编号组织答案

回答："""

    prompt = ChatPromptTemplate.from_template(template)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    question = "常用的嵌入模型有哪些？"
    print(f"\n❓ 问题: {question}")
    print("-" * 40)
    
    answer = rag_chain.invoke(question)
    print(f"💬 回答:\n{answer}")


def demo_rag_with_mmr():
    """
    结合 MMR 检索
    """
    print("\n" + "=" * 60)
    print("5️⃣ 结合 MMR 检索策略")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    vectordb = create_vectorstore()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    # 使用 MMR 检索器
    mmr_retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 3,
            "fetch_k": 5,
            "lambda_mult": 0.7
        }
    )
    
    template = """根据以下上下文回答问题：

{context}

问题：{question}

回答："""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    rag_chain = (
        {"context": mmr_retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    question = "构建 RAG 系统需要哪些组件？"
    print(f"\n❓ 问题: {question}")
    print("-" * 40)
    
    # 先看看检索到了什么
    docs = mmr_retriever.invoke(question)
    print("\n📚 检索到的来源（MMR 保证多样性）:")
    for i, doc in enumerate(docs):
        print(f"   {i+1}. [{doc.metadata['topic']}] {doc.page_content[:40]}...")
    
    answer = rag_chain.invoke(question)
    print(f"\n💬 回答:\n{answer}")


def demo_lcel_explanation():
    """
    LCEL 语法说明
    """
    print("\n" + "=" * 60)
    print("6️⃣ LCEL 语法说明")
    print("=" * 60)
    
    print("""
📚 LCEL（LangChain Expression Language）

LCEL 是 LangChain 推荐的链式调用方式，使用 | 操作符连接组件。

基本语法：
```python
chain = component1 | component2 | component3
result = chain.invoke(input)
```

RAG 链示例：
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def format_docs(docs):
    return "\\n\\n".join(doc.page_content for doc in docs)

prompt = ChatPromptTemplate.from_template('''
根据以下上下文回答问题：
{context}

问题：{question}
''')

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("你的问题")
```

优势：
✅ 代码更简洁
✅ 支持流式输出
✅ 易于调试和测试
✅ 灵活组合组件
    """)


def demo_interactive():
    """
    交互式问答演示
    """
    print("\n" + "=" * 60)
    print("7️⃣ 交互式问答")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    vectordb = create_vectorstore()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    
    template = """根据以下上下文回答问题。如果上下文中没有相关信息，请说"抱歉，我没有找到相关信息"。

上下文：
{context}

问题：{question}

回答："""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    print("\n🤖 RAG 问答系统已就绪！")
    print("   输入问题进行问答，输入 'q' 退出")
    print("-" * 40)
    
    while True:
        question = input("\n❓ 你的问题: ").strip()
        
        if question.lower() == 'q':
            print("👋 再见！")
            break
        
        if not question:
            continue
        
        answer = rag_chain.invoke(question)
        print(f"\n💬 回答:\n{answer}")


def main():
    """主函数"""
    print("=" * 60)
    print("💬 RAG 问答链演示（LCEL 方式）")
    print("=" * 60)
    
    print("""
💡 什么是 LCEL？

LCEL（LangChain Expression Language）是 LangChain 新版本
推荐的链式调用方式，使用管道操作符 | 连接组件。

使用场景：
- 企业知识库问答
- 文档智能助手
- 客服机器人
- 学习辅助工具
    """)
    
    # 运行演示
    demo_rag_flow()
    demo_lcel_explanation()
    demo_basic_rag()
    demo_custom_prompt()
    demo_rag_with_sources()
    demo_rag_with_mmr()
    
    # 交互式问答（可选）
    try:
        response = input("\n是否进入交互式问答？(y/n): ").strip().lower()
        if response == 'y':
            demo_interactive()
    except:
        pass
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("""
📝 下一步：
- 学习对话式 RAG（带记忆功能）
- 参见 07_conversational/conversational_chain.py
    """)


if __name__ == "__main__":
    main()