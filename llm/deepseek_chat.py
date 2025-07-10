# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="sk-9a1df2ae04284b648c2062773d573355", base_url="https://api.deepseek.com")

def deepseek_chat(prompt,text_with_history):
    messages=[
            {"role": "system", "content": prompt},
            # {"role": "user", "content": text},
        ]
    messages=messages+text_with_history
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )
    # print(response.choices[0].message.content)
    return response.choices[0].message.content
