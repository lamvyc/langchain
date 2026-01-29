"""
07_conversational/conversational_chain.py
==========================================
对话式 RAG 示例

本模块演示如何构建带记忆功能的对话式 RAG 系统，
支持多轮对话，能够理解上下文中的指代关系。

学习目标：
- 理解对话记忆的作用
- 掌握使用 LCEL 构建对话式 RAG
- 学会管理对话历史
"""

import os
from typing import List, Dict, Any

from dotenv import load_dotenv
load_dotenv()

# LangChain 组件
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document


# 准备知识库文档
KNOWLEDGE_BASE = [
    Document(
        page_content="""
LangChain 是一个用于构建 LLM 应用的开源框架。
主要功能：
- 提供标准化的 LLM 接口
- 支持提示模板管理
- 内置向量存储集成
- 提供 Chain 和 Agent 抽象
- 支持记忆（Memory）管理

安装方式：pip install langchain langchain-openai
""",
        metadata={"source": "langchain_intro"}
    ),
    Document(
        page_content="""
LangChain 的核心概念包括：
1. Model：语言模型（LLM、Chat Model）
2. Prompt：提示模板
3. Chain：将多个组件链接在一起
4. Agent：让 LLM 决定采取什么行动
5. Memory：存储对话历史
6. Retriever：从数据源检索信息
""",
        metadata={"source": "langchain_concepts"}
    ),
    Document(
        page_content="""
RAG（检索增强生成）的工作原理：
1. 索引阶段：将文档分块、向量化并存储
2. 检索阶段：将用户问题向量化，检索相似文档
3. 生成阶段：将检索结果作为上下文，让 LLM 生成答案

RAG 的优势：
- 减少幻觉
- 知识可更新
- 答案可追溯
""",
        metadata={"source": "rag_principle"}
    ),
    Document(
        page_content="""
Chroma 向量数据库使用指南：
1. 创建数据库：Chroma.from_documents(docs, embeddings)
2. 相似搜索：db.similarity_search(query, k=3)
3. MMR搜索：db.max_marginal_relevance_search(query)
4. 持久化：指定 persist_directory 参数
5. 元数据过滤：使用 filter 参数
""",
        metadata={"source": "chroma_guide"}
    ),
    Document(
        page_content="""
对话式 RAG 的关键点：
1. 历史管理：保存用户和AI的对话记录
2. 问题改写：将包含指代的问题改写为独立问题
3. 上下文传递：将历史对话作为上下文传递给模型
4. 记忆策略：选择合适的记忆方式（全量/窗口/摘要）

例如：用户问"它有什么功能？"，需要根据历史知道"它"指的是什么。
""",
        metadata={"source": "conversational_rag"}
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
    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(
        documents=KNOWLEDGE_BASE,
        embedding=embeddings,
    )
    return vectordb


def format_docs(docs):
    """格式化文档列表"""
    return "\n\n".join(doc.page_content for doc in docs)


def demo_why_memory():
    """
    为什么需要对话记忆
    """
    print("\n" + "=" * 60)
    print("1️⃣ 为什么需要对话记忆？")
    print("=" * 60)
    
    print("""
🤔 问题场景：

用户: "什么是 LangChain？"
助手: "LangChain 是一个用于构建 LLM 应用的框架..."

用户: "它有哪些核心概念？"  ← 这里的"它"指什么？
助手: ???

没有记忆的系统无法理解"它"指的是 LangChain！

✅ 有记忆的对话系统可以：
- 理解指代关系（它、这个、那个）
- 追踪对话主题
- 提供连贯的多轮对话体验
    """)


def demo_conversation_flow():
    """
    对话式 RAG 流程
    """
    print("\n" + "=" * 60)
    print("2️⃣ 对话式 RAG 流程")
    print("=" * 60)
    
    print("""
📊 对话式 RAG 流程图：

┌─────────────────┐
│    用户提问      │
└────────┬────────┘
         ↓
┌─────────────────┐     ┌─────────────────┐
│   对话历史       │ --> │   问题改写      │
│   (History)     │     │   (补全指代)    │
└─────────────────┘     └────────┬────────┘
                                 ↓
                        ┌─────────────────┐
                        │   向量检索      │
                        └────────┬────────┘
                                 ↓
┌─────────────────┐     ┌─────────────────┐
│   更新历史       │ <-- │   LLM 生成      │
└─────────────────┘     └────────┬────────┘
                                 ↓
                        ┌─────────────────┐
                        │   返回答案      │
                        └─────────────────┘

关键点：
- 问题改写：将"它"替换为"LangChain"
- 历史更新：保存本轮对话供后续使用
    """)


class ConversationManager:
    """对话管理器：管理对话历史"""
    
    def __init__(self, max_history: int = 10):
        self.history: List[Dict[str, str]] = []
        self.max_history = max_history
    
    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.history.append({"role": role, "content": content})
        # 保持历史在限制范围内
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history * 2:]
    
    def get_messages(self):
        """获取消息历史（LangChain 格式）"""
        messages = []
        for msg in self.history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        return messages
    
    def get_history_string(self):
        """获取历史的字符串格式"""
        if not self.history:
            return "无历史对话"
        
        history_str = ""
        for msg in self.history:
            role = "用户" if msg["role"] == "user" else "助手"
            history_str += f"{role}: {msg['content']}\n"
        return history_str.strip()
    
    def clear(self):
        """清空历史"""
        self.history = []


def demo_conversational_rag():
    """
    对话式 RAG 演示
    """
    print("\n" + "=" * 60)
    print("3️⃣ 对话式 RAG 演示")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    # 创建组件
    vectordb = create_vectorstore()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    retriever = vectordb.as_retriever(search_kwargs={"k": 2})
    
    # 创建对话管理器
    conversation = ConversationManager()
    
    # 问题改写提示（将包含指代的问题改写为独立问题）
    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个问题改写助手。根据对话历史，将用户的问题改写为一个独立的、不依赖上下文的问题。

对话历史：
{history}

如果用户问题已经是独立的，直接返回原问题。
只返回改写后的问题，不要其他内容。"""),
        ("human", "{question}")
    ])
    
    # 回答生成提示
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个专业的技术助手。根据以下上下文回答用户的问题。

上下文：
{context}

要求：
1. 只根据上下文回答
2. 如果上下文中没有相关信息，请明确说明
3. 回答简洁明了"""),
        ("human", "{question}")
    ])
    
    # 模拟多轮对话
    conversation_script = [
        "什么是 LangChain？",
        "它有哪些核心概念？",  # 使用"它"指代
        "其中的 RAG 是什么？",  # 追问细节
    ]
    
    print("\n🗣️ 多轮对话演示:")
    print("-" * 50)
    
    for i, question in enumerate(conversation_script, 1):
        print(f"\n【第 {i} 轮】")
        print(f"👤 用户: {question}")
        
        # 步骤1: 改写问题（如果有历史）
        if conversation.history:
            rewrite_chain = contextualize_prompt | llm | StrOutputParser()
            rewritten_question = rewrite_chain.invoke({
                "history": conversation.get_history_string(),
                "question": question
            })
            print(f"   🔄 改写后: {rewritten_question}")
        else:
            rewritten_question = question
        
        # 步骤2: 检索相关文档
        docs = retriever.invoke(rewritten_question)
        context = format_docs(docs)
        
        # 步骤3: 生成回答
        qa_chain = qa_prompt | llm | StrOutputParser()
        answer = qa_chain.invoke({
            "context": context,
            "question": rewritten_question
        })
        
        print(f"🤖 助手: {answer[:150]}...")
        
        # 步骤4: 更新历史
        conversation.add_message("user", question)
        conversation.add_message("assistant", answer)
    
    # 显示对话历史
    print("\n" + "-" * 50)
    print("📝 完整对话历史:")
    for msg in conversation.history:
        role = "👤" if msg["role"] == "user" else "🤖"
        print(f"   {role} {msg['content'][:50]}...")


def demo_memory_strategies():
    """
    记忆策略介绍
    """
    print("\n" + "=" * 60)
    print("4️⃣ 记忆策略介绍")
    print("=" * 60)
    
    print("""
📚 常用的记忆策略：

┌────────────────────────────┬────────────────────────────┐
│ 策略                        │ 特点                       │
├────────────────────────────┼────────────────────────────┤
│ 全量记忆                    │ 存储完整对话               │
│ (Buffer Memory)            │ ✅ 简单，信息完整          │
│                            │ ⚠️  长对话会超出上下文限制 │
├────────────────────────────┼────────────────────────────┤
│ 滑动窗口记忆                │ 只保留最近 k 轮对话        │
│ (Window Memory)            │ ✅ 控制上下文长度          │
│                            │ ⚠️  可能丢失早期信息       │
├────────────────────────────┼────────────────────────────┤
│ 摘要记忆                    │ 用 LLM 总结历史对话        │
│ (Summary Memory)           │ ✅ 长对话也能保持上下文    │
│                            │ ⚠️  需要额外 API 调用      │
├────────────────────────────┼────────────────────────────┤
│ 向量记忆                    │ 将历史存入向量库检索       │
│ (Vector Memory)            │ ✅ 可检索相关历史          │
│                            │ ⚠️  实现较复杂             │
└────────────────────────────┴────────────────────────────┘

选择建议：
- 短对话（<10轮）：全量记忆
- 中等对话（10-50轮）：滑动窗口
- 长对话或复杂场景：摘要记忆
    """)


def demo_window_memory():
    """
    滑动窗口记忆演示
    """
    print("\n" + "=" * 60)
    print("5️⃣ 滑动窗口记忆演示")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    vectordb = create_vectorstore()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    retriever = vectordb.as_retriever(search_kwargs={"k": 2})
    
    # 只保留最近 2 轮对话
    conversation = ConversationManager(max_history=2)
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", """根据上下文和对话历史回答问题。

上下文：
{context}

对话历史：
{history}"""),
        ("human", "{question}")
    ])
    
    questions = [
        "什么是 RAG？",
        "它有什么优势？",
        "Chroma 怎么用？",
        "前面说的 RAG 的优势有哪些？",  # 测试是否记得第2轮
    ]
    
    print("\n🗣️ 滑动窗口记忆演示 (max_history=2):")
    print("-" * 50)
    
    for i, q in enumerate(questions, 1):
        print(f"\n【第 {i} 轮】")
        print(f"👤 用户: {q}")
        
        docs = retriever.invoke(q)
        context = format_docs(docs)
        
        qa_chain = qa_prompt | llm | StrOutputParser()
        answer = qa_chain.invoke({
            "context": context,
            "history": conversation.get_history_string(),
            "question": q
        })
        
        print(f"🤖 助手: {answer[:120]}...")
        
        conversation.add_message("user", q)
        conversation.add_message("assistant", answer)
        
        # 显示当前记忆状态
        print(f"   📝 当前记忆: {len(conversation.history)//2} 轮对话")
    
    print("""
💡 观察：
- 第 4 轮提问时，第 1、2 轮的对话已经滑出窗口
- 系统可能无法准确回忆 RAG 的优势
    """)


def demo_interactive():
    """
    交互式对话演示
    """
    print("\n" + "=" * 60)
    print("6️⃣ 交互式对话")
    print("=" * 60)
    
    if not check_api_key():
        return
    
    vectordb = create_vectorstore()
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    retriever = vectordb.as_retriever(search_kwargs={"k": 2})
    conversation = ConversationManager()
    
    # 问题改写链
    contextualize_prompt = ChatPromptTemplate.from_messages([
        ("system", """根据对话历史，将问题改写为独立问题。

对话历史：
{history}

只返回改写后的问题。"""),
        ("human", "{question}")
    ])
    
    # 回答链
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", """根据上下文回答问题。

上下文：
{context}

对话历史：
{history}"""),
        ("human", "{question}")
    ])
    
    print("\n🤖 对话式 RAG 系统已就绪！")
    print("   - 输入问题进行对话")
    print("   - 输入 'clear' 清空记忆")
    print("   - 输入 'history' 查看对话历史")
    print("   - 输入 'q' 退出")
    print("-" * 50)
    
    while True:
        user_input = input("\n👤 你: ").strip()
        
        if user_input.lower() == 'q':
            print("👋 再见！")
            break
        
        if user_input.lower() == 'clear':
            conversation.clear()
            print("🗑️ 记忆已清空，开始新对话！")
            continue
        
        if user_input.lower() == 'history':
            print("\n📝 对话历史:")
            if not conversation.history:
                print("   (空)")
            for msg in conversation.history:
                role = "👤" if msg["role"] == "user" else "🤖"
                print(f"   {role} {msg['content'][:60]}...")
            continue
        
        if not user_input:
            continue
        
        # 改写问题
        if conversation.history:
            rewrite_chain = contextualize_prompt | llm | StrOutputParser()
            search_query = rewrite_chain.invoke({
                "history": conversation.get_history_string(),
                "question": user_input
            })
        else:
            search_query = user_input
        
        # 检索和回答
        docs = retriever.invoke(search_query)
        context = format_docs(docs)
        
        qa_chain = qa_prompt | llm | StrOutputParser()
        answer = qa_chain.invoke({
            "context": context,
            "history": conversation.get_history_string(),
            "question": user_input
        })
        
        print(f"\n?? 助手: {answer}")
        
        conversation.add_message("user", user_input)
        conversation.add_message("assistant", answer)


def main():
    """主函数"""
    print("=" * 60)
    print("🗣️ 对话式 RAG 演示")
    print("=" * 60)
    
    print("""
💡 对话式 RAG 是什么？

对话式 RAG = RAG + 对话记忆

特点：
- 支持多轮对话
- 理解上下文指代
- 追踪对话主题
- 提供连贯的交互体验

适用场景：
- 智能客服
- 知识库问答助手
- 学习辅导系统
- 企业内部助手
    """)
    
    # 运行演示
    demo_why_memory()
    demo_conversation_flow()
    demo_memory_strategies()
    demo_conversational_rag()
    demo_window_memory()
    
    # 交互式演示（可选）
    try:
        response = input("\n是否进入交互式对话？(y/n): ").strip().lower()
        if response == 'y':
            demo_interactive()
    except:
        pass
    
    print("\n" + "=" * 60)
    print("🎉 恭喜完成 LangChain + RAG 最佳实践学习！")
    print("=" * 60)
    print("""
📝 学习总结：

1. 文档加载（Loaders）- 加载各种格式的文档
2. 文本分割（Splitters）- 将文档分成合适的块
3. 向量嵌入（Embeddings）- 将文本转换为向量
4. 向量存储（VectorStores）- 存储和检索向量
5. 检索策略（Retrieval）- 相似度搜索、MMR、元数据过滤
6. 问答链（QA Chain）- 构建 RAG 问答流程
7. 对话式 RAG（Conversational）- 带记忆的多轮对话

🚀 下一步建议：
- 尝试不同的 LLM 和嵌入模型
- 探索更复杂的检索策略
- 构建自己的知识库应用
- 学习 LangChain Agent 和工具调用
    """)


if __name__ == "__main__":
    main()