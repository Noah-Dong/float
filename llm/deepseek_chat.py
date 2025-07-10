# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="xxx", base_url="https://api.deepseek.com")

def deepseek_chat(prompt,text):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        stream=False
    )
    # print(response.choices[0].message.content)
    return response.choices[0].message.content
