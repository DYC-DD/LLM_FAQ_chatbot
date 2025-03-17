from dotenv import load_dotenv
import os 
import json 
import openai 
import gradio as gr 

# 取得 OpenAI API key
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# 建立 OpenAI 客戶端 (此處使用假設的 openai.OpenAI 方式來建立客戶端)
client = openai.OpenAI(api_key=openai_api_key)

# 讀取 JSON 檔案
def load_json(file_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, file_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)
faq_data = load_json("data/faq.json")
rules_data = load_json("data/rules.json")

# 將 json 轉換為字串格式
faq_context = "\n".join([f"Q: {item['question']}\nA: {item['answer']}\n" for item in faq_data])
rules_context = "\n".join(rules_data["rules"])

# 設定 chat UI 畫面顯示提示詞
desc = ("電商客服機器人：可回答有關電商服務和政策的常見問題。輸入您的問題即可開始！\n\n"
        "使用說明：\n"
        "1. 輸入您的問題或查詢。\n"
        "2. 點擊提交後，機器人將根據 FAQ 提供回答。\n")

# 定義主要的客服機器人函數
def store_faq_bot(message, history):
    """
    根據用戶輸入的問題，從 FAQ 資料中提供相應的回答。
    """
    history_openai_format = [
        {
            "role": "system", 
            "content": f"""你是電商的 AI 客服，請基於以下FAQ內容回答客戶:
<FAQ>
{faq_context}
</FAQ>

重要規則：
{rules_context}
"""
        }
    ]
    
    # 將歷史對話紀錄加入
    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human})
        history_openai_format.append({"role": "assistant", "content": assistant})
    
    # 加入當前用戶問題
    history_openai_format.append({"role": "user", "content": message})
    
    # 呼叫 OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=history_openai_format,
        temperature=0.1,
        stream=True
    )
    
    # 逐步回應
    collected_messages = ""
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            chunk_text = chunk.choices[0].delta.content
            collected_messages += chunk_text
            yield collected_messages

# 關閉所有 Gradio 應用
gr.close_all()

# 啟動 Gradio 介面
gr.ChatInterface(
    fn=store_faq_bot,
    theme="soft",
    title="電商客服機器人",
    description=desc
).queue().launch(debug=True)
