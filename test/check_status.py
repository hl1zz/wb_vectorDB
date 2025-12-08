import weaviate

# 连接到本地的 Weaviate
client = weaviate.connect_to_local()

try:
    # 获取所有的 Collection (相当于关系型数据库里的表)
    collections = client.collections.list_all()
    
    if not collections:
        print("✅ 连接成功！")
        print("📭 当前仓库是空的，没有任何 Collection。")
    else:
        print(f"📚 发现 {len(collections)} 个 Collection:")
        for name in collections:
            print(f" - {name}")

finally:
    client.close()
