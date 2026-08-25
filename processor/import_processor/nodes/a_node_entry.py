import logging
from pathlib import Path

from processor.import_processor.base import BaseNode
from processor.import_processor.exceptions import StateFieldError, FileProcessingError
from processor.import_processor.state import ImportGraphState


class NodeEntry(BaseNode):
    """
    入口节点：任务分发
    """

    name = "node_entry"

    def process(self, state: ImportGraphState):
        logging.info(f"{self.name}节点开始执行")
        # 1.获得输入路径
        import_file_path = state.get("import_file_path")
        # 2.交验路径
        if not import_file_path:
            raise StateFieldError(field_name="import_file_path", expected_type=str)

        # 3.4 交验文件是否存在
        import_file_path_obj = Path(import_file_path)
        if not import_file_path_obj.exists():
            raise FileProcessingError(message=f"文件不存在：{import_file_path}")

        # 5.MD还是PDF
        if import_file_path_obj.suffix == ".md":
            state["is_md_read_enabled"] = True
            state["md_path"] = import_file_path
        elif import_file_path_obj.suffix == ".pdf":
            state["is_pdf_read_enabled"] = True
            state["pdf_path"] = import_file_path
        else:
            raise FileProcessingError(message=f"该文件的后缀格式{import_file_path_obj.suffix}不支持")

        state["file_title"] = import_file_path_obj.stem
        state["file_dir"] = r"E'\output"
        return state