import json

import logging
from typing import Dict, Any, List

from pymilvus import DataType, MilvusClient

from config.milvus_config import milvus_config
from processor.import_processor.base import BaseNode, setup_logging
from processor.import_processor.exceptions import StateFieldError, MilvusError
from processor.import_processor.state import ImportGraphState
from utils.milvus_utils import get_milvus_client, escape_milvus_string


class NodeImportMilvus(BaseNode):
    """
    导入向量库节点：数据持久化
    """

    name = "node_import_milvus"

    def process(self, state: ImportGraphState):

        # 1 数据集校验
        chunks_json_data, vector_dimension = self._step_1_check_inputs(state)

        # 2 客户端和集合名准备
        milvus_client = self._step_2_prepare_collection(vector_dimension)

        # 3 清理可能的冗余数据
        self._step_3_clean_old_data(milvus_client, chunks_json_data)

        # 4 数据入库（字段+索引）,返回向量库主键
        update_chunks = self._step_4_insert_data(milvus_client, chunks_json_data)
        for chunk in update_chunks:
            print(f"chunk_id:{chunk['chunk_id']}")

        # 5更新状态
        state["chunks"] = update_chunks

        return state

    def _step_1_check_inputs(self, state: Dict[str, Any]) -> tuple[List[Dict[str, Any]], int]:
        """
        数据校验
        """

        # 校验1：chunks非空
        print("node_import_milvus:步骤1：数据校验")
        chunks_json_data = state.get("chunks")

        if not chunks_json_data:
            raise StateFieldError(field_name="chunks", message="chunks不能为空", expected_type=list)

        if not isinstance(chunks_json_data, list):
            raise StateFieldError(field_name="chunks", message="chunks数据类型不正确", expected_type=list)

        # 校验2：切片包含dense_vector字段
        first_chunk = chunks_json_data[0]
        if 'dense_vector' not in first_chunk:
            raise StateFieldError(field_name="chunks", message="错误: 数据中缺失dense_vector字段")

        # 校验3：切片包含 sparse_vector 字段
        if 'sparse_vector' not in first_chunk:
            raise StateFieldError(field_name="chunks", message="错误: 数据中缺失sparse_vector字段")

        # 提取向量维度
        dimension = len(first_chunk['dense_vector'])
        return chunks_json_data, dimension

    def _step_2_prepare_collection(self, vector_dimension):
        """
        milvus客户端+集合准备
        """
        print("node_import_milvus:步骤2：创建客户端和集合")
        # 1 客户端
        milvus_client = get_milvus_client()

        # 2 集合
        collection_name = milvus_config.chunks_collection
        if not milvus_client.has_collection(collection_name):
            self.create_chunks_colletion(milvus_client, collection_name, vector_dimension)

        return milvus_client

    # 步骤2,方法1
    def create_chunks_colletion(self, milvus_client, colletion_name, vector_dimension):
        print(f"node_import_milvus：创建集合{colletion_name}")
        schema = milvus_client.create_schema(auto_id=True,enable_dynamic_field=True)

        # 字段声明
        schema.add_field(field_name="chunk_id",datatype=DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field(field_name="content", datatype=DataType.VARCHAR, max_length=65535)
        schema.add_field(field_name="title", datatype=DataType.VARCHAR, max_length=100)
        schema.add_field(field_name="parent_title", datatype=DataType.VARCHAR, max_length=100)
        schema.add_field(field_name="part", datatype=DataType.INT8)
        schema.add_field(field_name="file_title", datatype=DataType.VARCHAR, max_length=100)
        schema.add_field(field_name="item_name", datatype=DataType.VARCHAR, max_length=100)
        schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
        schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=vector_dimension)

        #索引声明
        index_params = milvus_client.prepare_index_params()
        index_params.add_index(
            field_name="dense_vector",
            index_name="dense_vector_index",
            index_type="AUTOINDEX",
            metric_type="COSINE"
        )
        index_params.add_index(
            field_name="sparse_vector",
            index_name="sparse_vector_index",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="IP",
            params={"inverted_index_algo": "DAAT_MAXSCORE", "normalize": True, "quantization": "none"}
        )

        # 创建集合
        milvus_client.create_collection(collection_name=colletion_name, schema=schema, index_params=index_params)

    def _step_3_clean_old_data(self, client, chunks_json_data):
        print("node_import_milvus:步骤3：清理旧数据")
        # 1. 获取查询条件
        file_title = chunks_json_data[0].get("file_title")

        # 2. 执行幂等清理
        self.clear_chunks_by_file_title(client, file_title)

    def clear_chunks_by_file_title(self, client, file_title):

        try:
            file_title = escape_milvus_string(file_title)
            client.delete(
                collection_name=milvus_config.chunks_collection,
                filter=f"file_title=='{file_title}'")
        except Exception as e:
            self.logger.error(f"Milvus 数据删除失败: {str(e)}")
            raise MilvusError(f"Milvus 数据删除失败: {str(e)}")

    def _step_4_insert_data(self, milvus_client, chunks_json_data):
        print("node_import_milvus:步骤4：插入数据")
        """
        批量插入milvus
        """
        # 1 数据处理
        data_to_insert = []
        for item in chunks_json_data:
            item_copy = item.copy()
            if "part" not in item_copy:
                item_copy["part"] = 0
            data_to_insert.append(item_copy)

        # 2 批量插入
        insert_result = milvus_client.insert(collection_name=milvus_config.chunks_collection, data=data_to_insert)
        insert_count = insert_result.get("insert_count")
        print(f"插入数据条数：{insert_count}")

        # 回写主键
        insert_ids = insert_result.get("ids")
        for index, item in enumerate(chunks_json_data):
            item["chunk_id"] = str(insert_ids[index])

        # 返回带有主键的chunks
        return chunks_json_data


if __name__ == "__main__":

    setup_logging()

    json_path = r"E:\output\H3C\H3C_new_new_new_chunks.json"
    with open(json_path, "r", encoding="utf-8") as f:
        state_json = f.read()

    state = json.loads(state_json)

    init_state = {
        "chunks": state
    }

    # 执行核心处理流程
    node_import_milvus = NodeImportMilvus()
    result = node_import_milvus(init_state)

    # logging.getLogger().info(json.dumps(result, ensure_ascii=False, indent=4))