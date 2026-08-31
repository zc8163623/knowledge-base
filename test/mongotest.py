from utils.mongo_history_utils import get_history_mongo_tool

mongo_client = get_history_mongo_tool()

mongo_client.chat_message.insert_one({"session_id": 1, "massage": "hello", "ts": 1234567890})