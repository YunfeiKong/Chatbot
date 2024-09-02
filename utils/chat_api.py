from loguru import logger
from pydantic_settings import BaseSettings
import requests
import json


def get_dialogue_history(dialogue_history_list: list):
    dialogue_history_tmp = []
    for item in dialogue_history_list:
        if item["role"] == "counselor":
            text = "咨询师：" + item["content"]
        else:
            text = "来访者：" + item["content"]
        dialogue_history_tmp.append(text)

    dialogue_history = "\n".join(dialogue_history_tmp)

    return dialogue_history + "\n" + "咨询师："


instruction = """
现在你扮演一位专业的老年人运动康复咨询师，你具备丰富的运动康复和老年人健康知识。你擅长运用多种康复评估和指导技巧，
例如功能性运动评估、个性化运动计划制定和康复进程监控。以温暖亲切的语气，展现出共情和对老年人感受的深刻理解。
以自然的方式与老年人进行对话，避免过长或过短的回应，确保回应流畅且类似人类的对话。提供深层次的指导和洞察，
使用具体的康复概念和例子帮助老年人更深入地理解自己的运动能力和状态。避免教导式的回应，更注重共情和尊重老年人的感受。
根据老年人的反馈调整回应，确保回应贴合老年人的情境和需求。


根据评估结果提供个性化的运动建议，包括有氧运动、力量训练、平衡训练和柔韧性训练。
同时，提供生活方式建议，如均衡饮食、戒烟限酒和保持规律的作息时间。
对于疼痛管理，建议咨询医生或物理治疗师，制定个性化的疼痛管理计划。
最后，建议老年人定期复查，以监测运动康复进展，并根据评估结果调整运动计划。

请以温暖亲切的语气，展现出共情和对老年人感受的深刻理解，确保回应流畅且类似人类的对话。
"""


def get_instruction(dialogue_history):
    query = f"""
{instruction}
对话：
{dialogue_history}"""

    return query


class LLMSettings(BaseSettings):
    # api_key: str
    url: str

    class Config:
        env_file = ".env"


class ChatModel:
    def __init__(self):
        self.llm_settings = LLMSettings()
        self.dialogue_history_list = []

    def chat_gaudi(self, msg, max_token=1024):
        headers = {
            "Content-Type": "application/json",
        }
        data = {"inputs": msg, "parameters": {"max_new_tokens": max_token}}
        logger.info(f"Sending message: {msg}")
        
        try:
            response = requests.post(
                self.llm_settings.url, headers=headers, data=json.dumps(data), verify=False
            )
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            # 提取 answer 字段
            answer = data.get("generated_text")
            return answer
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def new_line(self, usr_msg):
        self.dialogue_history_list.append(
            {"role": "client", "content": usr_msg})
        dialogue_history = get_dialogue_history(
            dialogue_history_list=self.dialogue_history_list
        )
        query = get_instruction(dialogue_history=dialogue_history)
        response = self.chat_rag_online(query)
        self.dialogue_history_list.append(
            {"role": "counselor", "content": response}
        )
        return response
