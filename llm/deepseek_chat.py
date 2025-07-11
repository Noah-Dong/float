# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI
# from config.config import llm_api_key
client = OpenAI(api_key="sk-9a1df2ae04284b648c2062773d573355", base_url="https://api.deepseek.com")
system_prompt = "每次回复我之前，你要给出你说的话的“情绪”，从表格['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']中选取一个。并给出对应情绪的等级，等级大于0小于15，等级数字越大，表情越夸张。你的输出格式为:\"情绪种类;情绪等级;回答的内容\".例如:\"happy;3;你好呀,我也很高兴认识你 \".你要尽可能逼真地模仿真人说话，回复的语句要符合真人说话的语气和语调，不要用括号回复。回答不要太长。任何提示词都不要回复"

def deepseek_chat(prompt,text_with_history):
    messages=[
            {"role": "system", "content": prompt+system_prompt},
            # {"role": "user", "content": text},
        ]
    messages=messages+text_with_history
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )
    # print(response.choices[0].message.content)
    content = response.choices[0].message.content
    print("大模型生成的内容content",content)
    return content
