import weaviate
import weaviate.classes.query as wvq
import sys

# ================= 配置区域 =================
TOP_K = 2                               # 返回结果数量
COLLECTION_NAME = "KnowledgeBase"       # 集合名称

# 你的查询向量 (示例用 4维，实际请换成你的 embedding)
# 必须与你 import_data.py 里插入的向量维度一致
QUERY_VECTOR = [0.15, 0.25, 0.35, 0.45] 
# ===========================================

def run_query():
    # 连接到本地 Weaviate
    client = weaviate.connect_to_local()

    try:
        # 1. 安全检查: 集合是否存在
        if not client.collections.exists(COLLECTION_NAME):
            print(f"❌ 错误: 集合 '{COLLECTION_NAME}' 不存在，请先导入数据。")
            return

        collection = client.collections.get(COLLECTION_NAME)

        # 2. 自动检测距离度量方式 (Metric)
        # 这是为了确保相似度计算绝对正确，不乱套公式
        config = collection.config.get()
        
        # 获取距离类型 (例如 'cosine', 'l2-squared', 'dot')
        # 注意：Weaviate v4 的 config 对象结构可能略有不同，这里使用通用属性访问
        try:
            metric = config.vector_index_config.distance_metric.value
        except AttributeError:
            # 兼容不同的小版本写法
            metric = str(config.vector_index_config.distance_metric)
            
        print(f"⚙️  当前数据库使用的距离算法: {metric.upper()}")

        # 3. 执行搜索
        print(f"🔍 正在查询 (TOP {TOP_K})...")
        results = collection.query.near_vector(
            near_vector=QUERY_VECTOR,
            limit=TOP_K,
            # 返回距离和原始向量
            return_metadata=wvq.MetadataQuery(distance=True),
            include_vector=True 
        )

        if not results.objects:
            print("⚠️  没有找到匹配的结果。")
            return

        print("-" * 60)
        for i, obj in enumerate(results.objects):
            # 获取原始距离 (Weaviate 直接返回的数值)
            dist = obj.metadata.distance
            
            # --- 动态计算相似度 (根据 Metric 类型) ---
            similarity_str = ""
            
            if "cosine" in metric.lower():
                # Cosine Distance = 1 - Cosine Similarity
                # 所以: Similarity = 1 - Distance
                sim = 1 - dist
                similarity_str = f"{sim:.4f} (Cosine Similarity)"
                
            elif "l2" in metric.lower():
                # L2 距离 (欧氏距离) 没有标准的 0-1 相似度公式
                # 常用转换: 1 / (1 + dist)
                sim = 1 / (1 + dist)
                similarity_str = f"{sim:.4f} (1/(1+L2) Normalized)"
                
            elif "dot" in metric.lower():
                # Dot distance 在 Weaviate 中通常是负的点积
                sim = -1 * dist
                similarity_str = f"{sim:.4f} (Dot Product)"
            else:
                similarity_str = f"未知算法 ({metric})，无法自动计算相似度"

            # 获取存储的向量
            stored_vector = obj.vector.get('default')
            
            # 为了显示整洁，如果向量太长，截取前4位显示
            vector_len = len(stored_vector) if stored_vector else 0
            if stored_vector and vector_len > 4:
                vector_display = stored_vector[:4]
                vector_suffix = "..."
            else:
                vector_display = stored_vector
                vector_suffix = ""

            # 打印结果
            print(f"🏆 排名 #{i+1}")
            print(f"📝 文本: {obj.properties.get('text', '无文本内容')}")
            print(f"🔢 向量: {vector_display}{vector_suffix} (维度: {vector_len})")
            print(f"📏 原始距离 (Distance):   {dist:.6f}")
            print(f"❤️  换算相似度 (Score):    {similarity_str}")
            print("-" * 60)

    except Exception as e:
        print(f"❌ 发生异常: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_query()