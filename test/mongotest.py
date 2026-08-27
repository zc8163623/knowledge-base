import json

from pymongo import MongoClient

mogo_client = MongoClient("mongodb://192.168.10.150:27017")

db = mogo_client["test"]
# 创建集合
# db.create_collection("classes")

# 插入数据
# db["classes"].insert_one({"name":"0525", "age":1})

# 查询数据
find_result = db["classes"].find()
for doc in find_result:
    print(doc)
    print(doc["name"])