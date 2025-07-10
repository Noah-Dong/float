#coding=utf-8

'''
requires Python 3.6 or later

pip install asyncio
pip install websockets

'''
import warnings
warnings.filterwarnings("ignore")
import asyncio
import websockets
import uuid
import json
import gzip
import copy
import re
import asyncio
from tts.tts_websocket_demo import test_query, request_json, voice_type
import uuid
import gzip
import json
import copy
import os

out_dir = "tts/tts_out"

MESSAGE_TYPES = {11: "audio-only server response", 12: "frontend server response", 15: "error message from server"}
MESSAGE_TYPE_SPECIFIC_FLAGS = {0: "no sequence number", 1: "sequence number > 0",
                               2: "last message from server (seq < 0)", 3: "sequence number < 0"}
MESSAGE_SERIALIZATION_METHODS = {0: "no serialization", 1: "JSON", 15: "custom type"}
MESSAGE_COMPRESSIONS = {0: "no compression", 1: "gzip", 15: "custom compression method"}

appid = "2020231942"
token = "cXWnhxUvkjk3hikTYJNuaDaYJ53JiIgT"
cluster = "volcano_tts"
voice_type = "zh_female_meilinvyou_moon_bigtts"
host = "openspeech.bytedance.com"
api_url = f"wss://{host}/api/v1/tts/ws_binary"

# version: b0001 (4 bits)
# header size: b0001 (4 bits)
# message type: b0001 (Full client request) (4bits)
# message type specific flags: b0000 (none) (4bits)
# message serialization method: b0001 (JSON) (4 bits)
# message compression: b0001 (gzip) (4bits)
# reserved data: 0x00 (1 byte)
default_header = bytearray(b'\x11\x10\x11\x00')





async def query_one(text, out_wav):
    request_json = {
    "app": {
        "appid": appid,
        "token": token,
        "cluster": cluster
    },
    "user": {
        "uid": "2103646832"
    },
    "audio": {
        "voice_type": voice_type,
        "encoding": "wav",
        "speed_ratio": 1.0,
        "volume_ratio": 1.0,
        "pitch_ratio": 1.0,
    },
    "request": {
        "reqid": "1111111",
        "text": text,
        "text_type": "plain",
        "operation": "query"
    }
}
    query_request_json = copy.deepcopy(request_json)
    query_request_json["audio"]["voice_type"] = voice_type
    query_request_json["request"]["reqid"] = str(uuid.uuid4())
    query_request_json["request"]["operation"] = "query"
    payload_bytes = str.encode(json.dumps(query_request_json))
    payload_bytes = gzip.compress(payload_bytes)  # if no compression, comment this line
    full_client_request = bytearray(default_header)
    full_client_request.extend((len(payload_bytes)).to_bytes(4, 'big'))  # payload size(4 bytes)
    full_client_request.extend(payload_bytes)  # payload
    print("\n------------------------ test 'query' -------------------------")
    print("request json: ", query_request_json)
    print("\nrequest bytes: ", full_client_request)
    file_to_save = open(out_wav, "wb")
    header = {"Authorization": f"Bearer; {token}"}
    async with websockets.connect(api_url, extra_headers=header, ping_interval=None) as ws:
        await ws.send(full_client_request)
        res = await ws.recv()
        parse_response(res, file_to_save)
        file_to_save.close()
        print("\nclosing the connection...")


def parse_response(res, file):
    print("--------------------------- response ---------------------------")
    # print(f"response raw bytes: {res}")
    protocol_version = res[0] >> 4
    header_size = res[0] & 0x0f
    message_type = res[1] >> 4
    message_type_specific_flags = res[1] & 0x0f
    serialization_method = res[2] >> 4
    message_compression = res[2] & 0x0f
    reserved = res[3]
    header_extensions = res[4:header_size*4]
    payload = res[header_size*4:]
    print(f"            Protocol version: {protocol_version:#x} - version {protocol_version}")
    print(f"                 Header size: {header_size:#x} - {header_size * 4} bytes ")
    print(f"                Message type: {message_type:#x} - {MESSAGE_TYPES[message_type]}")
    print(f" Message type specific flags: {message_type_specific_flags:#x} - {MESSAGE_TYPE_SPECIFIC_FLAGS[message_type_specific_flags]}")
    print(f"Message serialization method: {serialization_method:#x} - {MESSAGE_SERIALIZATION_METHODS[serialization_method]}")
    print(f"         Message compression: {message_compression:#x} - {MESSAGE_COMPRESSIONS[message_compression]}")
    print(f"                    Reserved: {reserved:#04x}")
    if header_size != 1:
        print(f"           Header extensions: {header_extensions}")
    if message_type == 0xb:  # audio-only server response
        if message_type_specific_flags == 0:  # no sequence number as ACK
            print("                Payload size: 0")
            return False
        else:
            sequence_number = int.from_bytes(payload[:4], "big", signed=True)
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            payload = payload[8:]
            print(f"             Sequence number: {sequence_number}")
            print(f"                Payload size: {payload_size} bytes")
        file.write(payload)
        if sequence_number < 0:
            return True
        else:
            return False
    elif message_type == 0xf:
        code = int.from_bytes(payload[:4], "big", signed=False)
        msg_size = int.from_bytes(payload[4:8], "big", signed=False)
        error_msg = payload[8:]
        if message_compression == 1:
            error_msg = gzip.decompress(error_msg)
        error_msg = str(error_msg, "utf-8")
        print(f"          Error message code: {code}")
        print(f"          Error message size: {msg_size} bytes")
        print(f"               Error message: {error_msg}")
        return True
    elif message_type == 0xc:
        msg_size = int.from_bytes(payload[:4], "big", signed=False)
        payload = payload[4:]
        if message_compression == 1:
            payload = gzip.decompress(payload)
        print(f"            Frontend message: {payload}")
    else:
        print("undefined message type!")
        return True

# 分句函数
def split_text(text):
    # 按中文句号、问号、感叹号、英文句号等分割
    return [s for s in re.split(r'[。！？!.~() ]', text) if s.strip()]

async def batch_query(long_text):
    sentences = split_text(long_text)
    out_files = []
    for idx, sent in enumerate(sentences):
        out_wav = os.path.join(out_dir, f"out_{idx}.wav")
        await query_one(sent, out_wav)
        out_files.append(out_wav)
    print("所有分句音频已生成：", out_files)
    # 可选：拼接音频
    from pydub import AudioSegment
    combined = AudioSegment.empty()
    for f in out_files:
        combined += AudioSegment.from_wav(f)
    combined.export(os.path.join(out_dir, "final.wav"), format="wav")

    return str(os.path.join(out_dir, "final.wav"))

if __name__ == '__main__':
    long_text = "心跳快得像是要冲破胸口了，他怎么敢这样突然要我亲他？我明明该推开他的，可那双眼睛望过来的时候，指尖都发麻了。笨蛋笨蛋笨蛋，我为什么要听他的啊！嘴唇碰到他温度的时候连呼吸都要烧起来了，现在耳朵肯定红得不像话……他会不会觉得我太主动了？可谁让他故意逗我妹妹的，活该被我盖章定下。等下，他该不会觉得我很好欺负吧？不行，必须装得更凶一点，绝对不能让这家伙发现我紧张得快要晕过去了。明明是我在驯服他，怎么反而像被他牵着鼻子走了？可恶的大坏蛋，以后绝对要加倍讨回来！"
    asyncio.run(batch_query(long_text))
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     # loop.run_until_complete(test_submit())
#     loop.run_until_complete(test_query("11111","1111.wav"))
