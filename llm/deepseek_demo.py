# Please install OpenAI SDK first: `pip3 install openai`
import time
from openai import OpenAI

client = OpenAI(api_key="sk-4a3ead4f23d54fc396038922444372fd", base_url="https://api.deepseek.com")

start_time = time.time()
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=True
)

full_content = ""
for chunk in response:
    if hasattr(chunk.choices[0].delta, "content") and chunk.choices[0].delta.content:
        delta = chunk.choices[0].delta.content
        print(delta, end="", flush=True)
        full_content += delta

end_time = time.time()
print()  # 换行
print(f"Time taken: {end_time - start_time} seconds")
