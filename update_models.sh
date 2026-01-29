#!/bin/bash
# 批量更新所有示例文件中的嵌入模型为 SiliconFlow 支持的模型
# chmod +x update_models.sh && ./update_models.sh

echo "🔄 更新项目中的嵌入模型配置..."

# 更新 04_vectorstores/chroma_demo.py
sed -i '' 's/OpenAIEmbeddings()/OpenAIEmbeddings(model="BAAI\/bge-large-zh-v1.5")/g' 04_vectorstores/chroma_demo.py

# 更新 05_retrieval/*.py
sed -i '' 's/OpenAIEmbeddings()/OpenAIEmbeddings(model="BAAI\/bge-large-zh-v1.5")/g' 05_retrieval/*.py

# 更新 06_qa_chain/retrieval_qa.py
sed -i '' 's/OpenAIEmbeddings()/OpenAIEmbeddings(model="BAAI\/bge-large-zh-v1.5")/g' 06_qa_chain/retrieval_qa.py

# 更新 07_conversational/conversational_chain.py
sed -i '' 's/OpenAIEmbeddings()/OpenAIEmbeddings(model="BAAI\/bge-large-zh-v1.5")/g' 07_conversational/conversational_chain.py

echo "✅ 更新完成！"
echo ""
echo "📝 已更新的文件："
echo "   - 04_vectorstores/chroma_demo.py"
echo "   - 05_retrieval/*.py (3个文件)"
echo "   - 06_qa_chain/retrieval_qa.py"
echo "   - 07_conversational/conversational_chain.py"