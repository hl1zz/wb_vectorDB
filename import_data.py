import weaviate
import weaviate.classes.config as wvc
from weaviate.util import generate_uuid5 # 引入生成固定UUID的工具
import json
import os
import sys

# ================= 配置区域 =================
COLLECTION_NAME = "weiboDb"         # 集合名称
DATA_FILE = "data.json"             # 数据文件名
# ===========================================

def main():
    # 1. 检查数据文件
    if not os.path.exists(DATA_FILE):
        print(f"❌ 错误: 未找到 {DATA_FILE}。请确保 JSON 文件在当前目录下。")
        sys.exit(1)

    print("🚀 正在连接 Weaviate...")
    client = weaviate.connect_to_local()

    try:
        # 2. 检查并创建集合 (如果不存在)
        if not client.collections.exists(COLLECTION_NAME):
            print(f"📦 集合 '{COLLECTION_NAME}' 不存在，正在创建...")
            
            client.collections.create(
                name=COLLECTION_NAME,
                # 【关键】设置为 None，表示自带向量
                vectorizer_config=wvc.Configure.Vectorizer.none(), 
                # 【关键】显式指定 HNSW 索引
                vector_index_config=wvc.Configure.VectorIndex.hnsw(
                    distance_metric=wvc.VectorDistances.COSINE
                ),
                properties=[
                    # 你的 String 数据存在这里
                    wvc.Property(name="text", data_type=wvc.DataType.TEXT),
                ]
            )
            print("✅ 集合创建成功！")
        else:
            print(f"ℹ️  集合 '{COLLECTION_NAME}' 已存在，准备导入数据 (相同内容将自动覆盖更新)...")

        # 3. 读取 JSON 数据
        print(f"📖 正在读取 {DATA_FILE}...")
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data_list = json.load(f)

        if not isinstance(data_list, list):
            print("❌ 数据格式错误: JSON 必须是一个列表 [...]")
            return

        # 4. 批量导入
        print(f"🔄 开始导入 {len(data_list)} 条数据...")
        collection = client.collections.get(COLLECTION_NAME)
        
        # 使用 dynamic batch 自动管理导入速度
        with collection.batch.dynamic() as batch:
            for i, item in enumerate(data_list):
                # --- 数据清洗与分离 ---
                # 1. 提取向量 (必须存在)
                vector = item.get("vector")
                if not vector:
                    print(f"⚠️  警告: 第 {i+1} 条数据缺少 'vector' 字段，已跳过。")
                    continue
                
                # 2. 提取文本内容 (关键：用于生成去重 UUID)
                # 假设你的 JSON key 是 "text"。如果是别的，请修改这里
                text_content = item.get("text")
                if not text_content:
                     # 如果没有 text，无法生成去重ID，你可以选择跳过，或者随机生成
                     # 这里选择跳过以保证数据质量
                     print(f"⚠️  警告: 第 {i+1} 条数据缺少 'text' 字段，无法生成唯一ID，已跳过。")
                     continue

                # 3. 提取其他属性
                properties = {k: v for k, v in item.items() if k != "vector"}
                
                # --- 核心修改：生成确定性 UUID ---
                # 只要 text_content 一样，这个 uuid 就永远一样
                # Weaviate 遇到相同的 uuid 会执行 "Update" 而不是 "Create"
                deterministic_uuid = generate_uuid5(text_content)

                # 4. 添加到批处理队列
                batch.add_object(
                    properties=properties,
                    vector=vector,
                    uuid=deterministic_uuid  # <--- 指定 UUID
                )

        # 5. 错误统计
        failed_objs = client.batch.failed_objects
        if len(failed_objs) > 0:
            print(f"❌ 完成，但有 {len(failed_objs)} 条失败。")
            print(f"   错误示例: {failed_objs[0].message}")
        else:
            print(f"✅ 完美！处理了 {len(data_list)} 条数据 (重复数据已自动合并)。")
            
            # 打印当前数据库里的实际条数，验证去重效果
            actual_count = collection.aggregate.over_all(total_count=True).total_count
            print(f"📊 当前数据库实际存储总数: {actual_count}")

    except Exception as e:
        print(f"❌ 发生异常: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()