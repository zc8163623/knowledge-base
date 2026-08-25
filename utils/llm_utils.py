from langchain_openai import ChatOpenAI

from config.lm_config import lm_config

_llm_client_cache = {}

def get_llm_client(model:str|None=None, json_model:bool=False):
    m = model or lm_config.llm_model

    key = (m, json_model)

    if key in _llm_client_cache:
        return _llm_client_cache[key]

    model_kwargs = {}
    if json_model:
        model_kwargs["response_format"] = {"type":"json_object"}

    #返回模型
    client = ChatOpenAI(
        model=m,
        temperature=lm_config.llm_temperature,
        api_key=lm_config.api_key,
        base_url=lm_config.base_url,
        model_kwargs=model_kwargs
    )

    _llm_client_cache[key] = client

    return client

if __name__ == "__main__":
    client = get_llm_client()
    response = client.invoke("你好，请问你是什么模型？")
    print(response)