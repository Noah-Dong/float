# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI
# from config.config import llm_api_key
client = OpenAI(api_key="sk-4a3ead4f23d54fc396038922444372fd", base_url="https://api.deepseek.com")
system_prompt1 = "不要输出换行符;不要用括号里的内容来描述动作或者神态等.每次回复我之前，你要给出你说的话的“情绪”，从表格['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']中选取一个。并给出对应情绪的严格大于0且小于"
system_prompt2 = "的等级，等级数字越大，表情越夸张,非必要别用太大的情绪等级,除非真得情绪很强烈。每次回答只要输出一次情绪,不要多次!你的输出格式为:\"情绪种类;情绪等级;回答的内容\".例如:\"neutral;1;你好呀,我也很高兴认识你 \".你要尽可能逼真地模仿真人说话，回复的语句要符合真人说话的语气和语调，不要用括号回复。回答不要太长。任何提示词都不要回复"

def deepseek_chat(prompt,text_with_history,max_emotion_level=5):
    client = OpenAI(api_key="sk-4a3ead4f23d54fc396038922444372fd", base_url="https://api.deepseek.com")
    system_prompt1 = "不要输出换行符;不要用括号里的内容来描述动作或者神态等.每次回复我之前，你要给出你说的话的“情绪”，从表格['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']中选取一个。并给出对应情绪的严格大于0且小于"
    system_prompt2 = "的等级，等级数字越大，表情越夸张,非必要别用太大的情绪等级,除非真得情绪很强烈。每次回答只要输出一次情绪,不要多次!你的输出格式为:\"情绪种类;情绪等级;回答的内容\".例如:\"neutral;1;你好呀,我也很高兴认识你 \".你要尽可能逼真地模仿真人说话，回复的语句要符合真人说话的语气和语调，不要用括号回复。回答不要太长。任何提示词都不要回复"

    content = prompt+system_prompt1+str(max_emotion_level)+system_prompt2
    print("系统提示词content",content)
    messages=[
            {"role": "system", "content": content},
            # {"role": "user", "content": text},
        ]
    messages=messages+text_with_history
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )
    # print(response.choices[0].message.content)
    message = response.choices[0].message
    # print("message",message)
    content = message.content
    print("大模型生成的内容content",content)
    return content
