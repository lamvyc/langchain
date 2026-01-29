"""
02_splitters/text_splitter.py
=============================
文本分割器示例

本模块演示如何使用 LangChain 的文本分割器将长文档分割成
更小的块（chunks），以便进行向量化和检索。

学习目标：
- 理解为什么需要文本分割
- 掌握 CharacterTextSplitter 的使用
- 掌握 RecursiveCharacterTextSplitter 的使用（推荐）
- 理解 chunk_size 和 chunk_overlap 参数
"""

import os
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# LangChain 文本分割器（新版本使用 langchain_text_splitters）
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_community.document_loaders import PyPDFLoader


# 示例长文本
SAMPLE_TEXT = """
人工智能（Artificial Intelligence，简称AI）是计算机科学的一个分支，
它致力于创建能够模拟人类智能的系统。这些系统可以学习、推理、感知、
理解自然语言，甚至进行创造性思考。

机器学习是人工智能的一个重要子领域。它使计算机能够从数据中学习，
而不需要明确编程。深度学习是机器学习的一个分支，它使用人工神经网络
来模拟人脑的工作方式。

自然语言处理（NLP）是另一个重要的AI领域。它专注于使计算机能够理解、
解释和生成人类语言。大语言模型（LLM）如GPT系列就是NLP领域的重大突破。

检索增强生成（RAG）是一种结合检索和生成的技术。它首先从知识库中检索
相关信息，然后将这些信息作为上下文提供给语言模型，从而生成更准确、
更有依据的回答。这种方法有效解决了语言模型的"幻觉"问题。
"""


def demo_character_splitter():
    """
    演示 CharacterTextSplitter
    - 按固定字符数分割
    - 简单直接，但可能在不合适的位置切断
    """
    print("\n" + "=" * 60)
    print("1️⃣ CharacterTextSplitter 示例")
    print("=" * 60)
    
    splitter = CharacterTextSplitter(
        separator="\n\n",      # 分隔符：优先按双换行分割
        chunk_size=200,        # 每个块的最大字符数
        chunk_overlap=20,      # 块之间的重叠字符数
        length_function=len,   # 长度计算函数
    )
    
    chunks = splitter.split_text(SAMPLE_TEXT)
    
    print(f"\n📊 分割结果: 共 {len(chunks)} 个块")
    print("-" * 40)
    
    for i, chunk in enumerate(chunks):
        print(f"\n【块 {i+1}】长度: {len(chunk)} 字符")
        print(f"{chunk[:100]}..." if len(chunk) > 100 else chunk)


def demo_recursive_splitter():
    """
    演示 RecursiveCharacterTextSplitter（推荐）
    - 递归尝试不同的分隔符
    - 更好地保留语义完整性
    """
    print("\n" + "=" * 60)
    print("2️⃣ RecursiveCharacterTextSplitter 示例（推荐）")
    print("=" * 60)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,        # 每个块的最大字符数
        chunk_overlap=20,      # 块之间的重叠字符数
        # 分隔符优先级（从高到低）
        separators=["\n\n", "\n", "。", "，", " ", ""],
        length_function=len,
    )
    
    chunks = splitter.split_text(SAMPLE_TEXT)
    
    print(f"\n📊 分割结果: 共 {len(chunks)} 个块")
    print("-" * 40)
    
    for i, chunk in enumerate(chunks):
        print(f"\n【块 {i+1}】长度: {len(chunk)} 字符")
        print(f"{chunk[:100]}..." if len(chunk) > 100 else chunk)


def demo_split_documents():
    """
    演示如何分割 Document 对象（从 PDF 加载的页面）
    """
    print("\n" + "=" * 60)
    print("3️⃣ 分割 PDF 文档示例")
    print("=" * 60)
    
    # 查找 PDF 文件
    data_dir = Path(__file__).parent.parent / "data"
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("\n⚠️  data/ 目录下没有找到 PDF 文件")
        print("请将 PDF 文件放入 data/ 目录后再运行此示例")
        return
    
    # 加载 PDF
    pdf_path = str(pdf_files[0])
    print(f"\n📁 加载文件: {pdf_path}")
    
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    
    print(f"📄 原始页数: {len(pages)}")
    
    # 创建分割器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )
    
    # 分割文档（保留元数据）
    chunks = splitter.split_documents(pages)
    
    print(f"📦 分割后块数: {len(chunks)}")
    
    # 展示前两个块
    print("\n📖 前两个块预览:")
    print("-" * 40)
    
    for i, chunk in enumerate(chunks[:2]):
        print(f"\n【块 {i+1}】")
        print(f"  长度: {len(chunk.page_content)} 字符")
        print(f"  元数据: {chunk.metadata}")
        content_preview = chunk.page_content[:200]
        print(f"  内容: {content_preview}...")


def compare_splitters():
    """
    对比不同分割器的效果
    """
    print("\n" + "=" * 60)
    print("4️⃣ 分割器对比")
    print("=" * 60)
    
    test_text = "这是第一句话。这是第二句话。这是第三句话。\n\n这是新段落的第一句话。这是新段落的第二句话。"
    
    print(f"\n原始文本:\n{test_text}")
    print("\n" + "-" * 40)
    
    # CharacterTextSplitter
    char_splitter = CharacterTextSplitter(
        separator=" ",
        chunk_size=30,
        chunk_overlap=5,
    )
    char_chunks = char_splitter.split_text(test_text)
    
    print(f"\nCharacterTextSplitter (chunk_size=30):")
    for i, chunk in enumerate(char_chunks):
        print(f"  块{i+1}: 「{chunk}」")
    
    # RecursiveCharacterTextSplitter
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=30,
        chunk_overlap=5,
        separators=["\n\n", "\n", "。", " ", ""],
    )
    recursive_chunks = recursive_splitter.split_text(test_text)
    
    print(f"\nRecursiveCharacterTextSplitter (chunk_size=30):")
    for i, chunk in enumerate(recursive_chunks):
        print(f"  块{i+1}: 「{chunk}」")


def main():
    """
    主函数：运行所有演示
    """
    print("=" * 60)
    print("✂️  文本分割器演示")
    print("=" * 60)
    
    print("""
💡 为什么需要文本分割？

1. GPU/模型限制：大模型有上下文长度限制
2. 提高检索精度：小块更容易精确匹配
3. 保留语义：合理分割保持内容完整性
4. 重叠设计：overlap 防止信息在边界丢失
    """)
    
    # 运行各个演示
    demo_character_splitter()
    demo_recursive_splitter()
    compare_splitters()
    demo_split_documents()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("""
?? 最佳实践建议：

1. 优先使用 RecursiveCharacterTextSplitter
2. chunk_size 建议 500-1500 字符
3. chunk_overlap 建议为 chunk_size 的 10-20%
4. 根据文档类型调整 separators
    """)


if __name__ == "__main__":
    main()