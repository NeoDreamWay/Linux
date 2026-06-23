"""
功能：
1. 读取CSV流量数据（若不存在则生成示例数据）
2. 提取 PacketCount 与 Bytes 特征
3. 使用 KMeans 聚类
4. 输出异常流量（距离聚类中心较远）
"""

import os
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

FILE = "traffic.csv"

if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    np.random.seed(42)
    normal = pd.DataFrame({
        "PacketCount": np.random.randint(50, 300, 95),
        "Bytes": np.random.randint(1000, 8000, 95)
    })
    abnormal = pd.DataFrame({
        "PacketCount": [900, 1100, 1500, 1300, 1800],
        "Bytes": [50000, 62000, 85000, 71000, 99000]
    })
    df = pd.concat([normal, abnormal], ignore_index=True)

X = df[["PacketCount", "Bytes"]]

model = KMeans(n_clusters=2, random_state=42, n_init=10)
labels = model.fit_predict(X)

centers = model.cluster_centers_
dist = np.linalg.norm(X.values - centers[labels], axis=1)

threshold = np.percentile(dist, 95)

df["Cluster"] = labels
df["Distance"] = dist
df["Anomaly"] = dist > threshold

print("===== 聚类结果 =====")
print(df.head())

print("\n===== 检测到的异常流量 =====")
print(df[df["Anomaly"]])

print(f"\n总样本数: {len(df)}")
print(f"异常数量: {df['Anomaly'].sum()}")