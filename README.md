# Weaviate 向量库本地部署指南

本项目提供了一个基于 Docker 的 Weaviate 向量数据库环境，以及配套的数据导入与查询脚本。支持 **“自带向量（Bring Your Own Vectors）”** 模式，适用于离线部署或私有化场景。
---

## 📋 目录结构

```
.
├── docker-compose.yml      # 数据库服务配置文件
├── requirements.txt        # Python 依赖库列表
├── import_data.py          # 数据导入脚本（自动建库 + 批量入库）
├── query_data.py           # 向量查询测试脚本
├── data.json               #源数据文件
└── weaviate_data/          # (启动后自动生成) 数据持久化目录
```

---

## 🛠️ 1. 环境准备

确保本机已安装以下组件：

- **Docker**（且已启动）
- **Python 3.8+**

### 安装 Python 依赖

在终端中进入本项目根目录，执行：

```bash
pip install -r requirements.txt
```

---

## 💾 2. 数据文件格式说明（关键）

在运行导入脚本前，请确保项目根目录下存在 `data.json` 文件。

### ✅ JSON 格式规范

- **文件位置**：必须与 `import_data.py` 在同一目录。
- **文件格式**：标准 JSON 数组 `[...]`
- **字段要求**：
  - `text`（String）：必填，原始文本内容。
  - `vector`（List[float]）：必填，对应文本的 embedding 向量。

### 📄 示例 `data.json`

```json
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
```

### ⚠️ 关键注意事项

- **维度一致性**：所有 `vector` 的长度必须完全相同（例如均为 768 维），否则导入将失败。
- **字段名称**：JSON 中的 key 必须严格为 `"text"` 和 `"vector"`。若使用其他名称（如 `content` 或 `embedding`），脚本将无法识别。

---

## 🚀 3. 部署与导入流程

> 💡 请务必先通过 `cd` 进入本项目目录，再执行以下命令。

### 第一步：启动数据库服务

```bash
docker-compose up -d
```

- 首次运行会自动拉取 Weaviate 镜像（如本地不存在）。
- **数据持久化**：数据将保存在 `weaviate_data/` 目录（由 Docker 卷管理），即使容器停止或系统重启，数据也不会丢失。

### 第二步：导入数据

确保 `data.json` 已准备就绪，运行：

```bash
python import_data.py
```

- 脚本将自动创建名为 `KnowledgeBase` 的集合（使用 HNSW 索引 + Cosine 距离）。
- 成功提示：  
  `✅ 完美！成功导入 X 条数据。`

---

## 🔎 4. 查询测试

导入完成后，可运行查询脚本验证检索功能：

```bash
python query_data.py
```

### 自定义查询向量

1. 用文本编辑器打开 `query_data.py`。
2. 找到如下行：
   ```python
   QUERY_VECTOR = [...]
   ```
3. 将其替换为你自己的查询向量（**维度必须与库中数据一致**）。
4. 保存文件并重新运行脚本，查看最相似结果及距离指标。

---

## 🛑 5. 停止服务

如需停止服务以释放资源：

```bash
docker-compose down
```

> 🔒 **数据安全提示**：此命令仅停止并删除容器，**不会删除持久化数据卷**。下次运行 `docker-compose up -d` 时，历史数据依然保留。


--- 
