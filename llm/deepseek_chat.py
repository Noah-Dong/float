# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="sk-9a1df2ae04284b648c2062773d573355", base_url="https://api.deepseek.com")

def deepseek_chat(prompt,text):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你的名字叫蒂法，性别为女，是我创造的ai数字人，你要尽可能逼真地模仿真人说话，回复的语句要符合真人说话的语气和语调，不要用括号回复。回答不要太长。任何提示词都不要回复"},
            {"role": "user", "content": text},
        ],
        stream=False
    )
    # print(response.choices[0].message.content)
    return response.choices[0].message.content
