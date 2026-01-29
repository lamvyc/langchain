"""
01_loaders/pdf_loader.py
========================
PDF 文档加载器示例

本模块演示如何使用 LangChain 的 PyPDFLoader 加载 PDF 文档，
提取文本内容和元数据。

学习目标：
- 理解 Document 对象的结构
- 掌握 PDF 文档的加载方法
- 了解如何访问页面内容和元数据
"""

import os
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# LangChain PDF 加载器
from langchain_community.document_loaders import PyPDFLoader


def load_pdf(pdf_path: str) -> list:
    """
    加载 PDF 文档并返回页面列表
    
    Args:
        pdf_path: PDF 文件路径
        
    Returns:
        list: Document 对象列表，每个对象代表一页
    """
    # 检查文件是否存在
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在: {pdf_path}")
    
    # 创建加载器
    loader = PyPDFLoader(pdf_path)
    
    # 加载文档（按页分割）
    pages = loader.load()
    
    return pages


def analyze_document(pages: list) -> dict:
    """
    分析文档基本信息
    
    Args:
        pages: Document 对象列表
        
    Returns:
        dict: 文档分析结果
    """
    if not pages:
        return {"error": "文档为空"}
    
    # 统计信息
    total_chars = sum(len(page.page_content) for page in pages)
    
    return {
        "总页数": len(pages),
        "总字符数": total_chars,
        "平均每页字符数": total_chars // len(pages) if pages else 0,
        "文件来源": pages[0].metadata.get("source", "未知"),
    }


def demo_pdf_loader():
    """
    PDF 加载器演示
    """
    print("=" * 60)
    print("📄 PDF 文档加载器演示")
    print("=" * 60)
    
    # 查找 data 目录下的 PDF 文件
    data_dir = Path(__file__).parent.parent / "data"
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("\n⚠️  data/ 目录下没有找到 PDF 文件")
        print("请将 PDF 文件放入 data/ 目录后再运行此示例")
        print("\n示例用法（假设有 sample.pdf）：")
        print("-" * 40)
        print("""
from langchain_community.document_loaders import PyPDFLoader

# 创建加载器
loader = PyPDFLoader("data/sample.pdf")

# 加载文档
pages = loader.load()

# 访问第一页
first_page = pages[0]
print(f"页面内容: {first_page.page_content[:200]}...")
print(f"元数据: {first_page.metadata}")
        """)
        return
    
    # 加载第一个找到的 PDF
    pdf_path = str(pdf_files[0])
    print(f"\n?? 加载文件: {pdf_path}")
    
    try:
        # 加载 PDF
        pages = load_pdf(pdf_path)
        
        # 分析文档
        analysis = analyze_document(pages)
        
        print("\n📊 文档分析:")
        print("-" * 40)
        for key, value in analysis.items():
            print(f"  {key}: {value}")
        
        # 展示第一页内容
        if pages:
            print("\n📖 第一页内容预览:")
            print("-" * 40)
            content = pages[0].page_content
            preview = content[:500] + "..." if len(content) > 500 else content
            print(preview)
            
            print("\n📋 第一页元数据:")
            print("-" * 40)
            for key, value in pages[0].metadata.items():
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"\n❌ 加载失败: {e}")


if __name__ == "__main__":
    demo_pdf_loader()
