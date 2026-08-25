import json
from pathlib import Path
from typing import Dict, List

from processor.import_processor.base import BaseNode
from processor.import_processor.exceptions import StateFieldError
from processor.import_processor.state import ImportGraphState
from utils.embedding_utils import generate_embeddings


class NodeBGEEmbedding(BaseNode):
    """
    混合向量化节点：使用 BGE-M3 模型将文本转换为向量
    """

    name = "node_bge_embedding"

    def process(self, state: ImportGraphState):
        # 1 参数校验
        chunks = self._step_1_validate_path(state)

        # 2 数据向量化
        output_data = self._step_2_generate_embeddings(chunks)
        for item in output_data:
            item_name = item.get("item_name")
            content = item.get("content")
            print(f"item_name:{item_name}\n{content}")
            sparse_vector = item["sparse_vector"]
            print(f"sparse_vector:{sparse_vector}")


        # 3 返回结果
        state["chunks"] = output_data

        return state

    # 步骤1
    def _step_1_validate_path(self, state):
        print("node_bge_embedding:步骤1：参数校验")
        chunks = state.get("chunks")
        if not chunks:
            raise ValueError("参数错误，chunks")
        if not isinstance(chunks, list):
            raise StateFieldError(field_name="chunks", message="chunks数据类型不正确", expected_type=list)

        return chunks
    # 步骤2
    def _step_2_generate_embeddings(self, chunks:List[Dict[str,str]])->List[Dict[str,str]]:
        """
        将item_name和content转化为向量数据（稀疏和稠密）
        """
        print("node_bge_embedding:步骤2：数据向量化")
        output_data = []
        batch_size = 5
        for i in range(0, len(chunks), batch_size):
            five_ready_texts = []
            five_text = chunks[i:i + batch_size] # 第一次从0取到4块，一共取5块
            for doc in five_text:
                item_name = doc.get("item_name")
                content = doc.get("content")
                five_ready_texts.append(f"{item_name}\n{content}" if item_name else content)

            embeddings = generate_embeddings(five_ready_texts)

            for j,doc in enumerate(five_text):
                item = doc.copy()
                dense = embeddings["dense"][j]
                sparse = embeddings["sparse"][j]
                item["dense_vector"] = dense
                item["sparse_vector"] = sparse
                output_data.append(item)

        return output_data

if __name__ == "__main__":
    node = NodeBGEEmbedding()
    path = r"E:\output\H3C\H3C_new_new_chunks.json"
    with open(path, "r", encoding="utf-8") as f:
        chunks_content = json.load(f)

    init_state = {
        "chunks": chunks_content
    }

    response = node(init_state)
    print(response)
    dumps = json.dumps(response, ensure_ascii=False,indent=4)
    print(dumps)