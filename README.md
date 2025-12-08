# Weaviate 向量库本地部署指南

本项目包含了一个基于 Docker 的 Weaviate 向量数据库环境，以及配套的数据导入与查询脚本。该环境支持“自带向量（Bring Your Own Vectors）”模式，适用于离线部署或私有化环境。

## 📋 目录结构

*   `docker-compose.yml`: 数据库服务配置文件
*   `requirements.txt`: Python 依赖库列表
*   `import_data.py`: 数据导入脚本（自动建库 + 批量入库）
*   `query_data.py`: 向量查询测试脚本
*   `data.json`: (需自行准备) 你的源数据文件
*   `weaviate_data/`: (启动后自动生成) 数据持久化目录

---

## 🛠️ 1. 环境准备

确保本机已安装：
1.  **Docker** (且已启动)
2.  **Python 3.8+**

### 安装 Python 依赖
打开终端，**通过 `cd` 命令进入本项目文件夹**，然后运行：

pip install -r requirements.txt



💾 2. 数据文件格式说明 (关键)
在运行导入脚本前，请确保在本项目根目录下存在一个名为 data.json 的文件。

JSON 格式规范
文件位置: 必须与 import_data.py 在同一级目录。
文件格式: 标准 JSON 数组 [...]
text (String): 必填。用于存储你的原始文本内容。
vector (List[float]): 必填。对应文本的向量 embedding 数组。
示例 data.json
JSON
[
    {
        "text": "这是第一段测试文本", 
        "vector": [0.123, 0.456, 0.789, 0.101]
    },
    {
        "text": "这是第二段测试文本", 
        "vector": [0.555, 0.666, 0.777, 0.888]
    }
]
⚠️ 关键注意事项
维度一致性: 数组中所有对象的 vector 长度必须完全一致（例如全部都是 768 维）。如果不一致，导入会报错。
字段名称: JSON 中的 Key 必须严格为 "text" 和 "vector"。如果你的数据 Key 是别的（如 content 或 embedding），脚本将无法识别。


🚀 3. 部署与导入流程
请务必在终端中通过 cd 命令进入当前项目文件夹，再执行以下步骤。

第一步：启动数据库服务
bash
docker-compose up -d
第一次启动时会自动拉取镜像（如果本地没有的话）。
关于数据持久化: 数据会自动保存在 Docker 的数据卷中。即使停止容器或重启电脑，只要不手动删除卷，数据都会永久保存。


第二步：导入数据
确保 data.json 准备好后，运行：

python import_data.py
脚本会自动创建名为 KnowledgeBase 的集合（配置为 HNSW 索引 + Cosine 距离）。
脚本会批量将数据写入数据库。
成功信号: 控制台输出 ✅ 完美！成功导入 X 条数据。


🔎 4. 查询测试
数据导入完成后，可以使用测试脚本来验证检索功能。

python query_data.py
如何自定义查询：
用文本编辑器打开 query_data.py。
找到 QUERY_VECTOR = [...] 这一行。
将其修改为你想要搜索的真实向量（维度必须与库中数据一致）。
保存并重新运行脚本，查看最相似的结果及距离指标。


🛑 5. 停止服务
如果不使用数据库，可以通过以下命令停止服务并释放内存：

docker-compose down
数据安全提示: 此命令只会停止并删除容器，不会删除数据卷。下次运行 docker-compose up -d 时，之前导入的数据依然存在。
