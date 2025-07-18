#coding=utf-8
import requests
import json
import time
import os
import uuid

s = requests

appid = '2020231942'
token = 'cXWnhxUvkjk3hikTYJNuaDaYJ53JiIgT'
cluster = 'volc_auc_common'
# audio_url = 'https://float-avatar-audio.oss-cn-shenzhen.aliyuncs.com/test_query.wav'
service_url = 'https://openspeech.bytedance.com/api/v1/auc'

headers = {'Authorization': 'Bearer; {}'.format(token)}

def submit_task():
    request = {
        "app": {
            "appid": appid,
            "token": token,
            "cluster": cluster
        },
        "user": {
            "uid": "388808087185088_demo"
        },
        "audio": {
            "format": "wav",
            "url": audio_url
        },
        "additions": {
            'with_speaker_info': 'False',
        }
    }

    r = s.post(service_url + '/submit', data=json.dumps(request), headers=headers)
    resp_dic = json.loads(r.text)
    print(resp_dic)
    id = resp_dic['resp']['id']
    print(id)
    return id


def query_task(task_id):
    query_dic = {}
    query_dic['appid'] = appid
    query_dic['token'] = token
    query_dic['id'] = task_id
    query_dic['cluster'] = cluster
    query_req = json.dumps(query_dic)
    # print("query_req\n",query_req)
    r = s.post(service_url + '/query', data=query_req, headers=headers)
    # print("query_task\n",r.text)
    resp_dic = json.loads(r.text)
    return resp_dic


def file_recognize(url):
    global audio_url
    audio_url=url
    task_id = submit_task()
    start_time = time.time()
    while True:
        time.sleep(2)
        # query result
        resp_dic = query_task(task_id)
        if resp_dic['resp']['code'] == 1000: # task finished
            print("success")
            print(resp_dic['resp']['text'])
            return resp_dic['resp']['text']
        elif resp_dic['resp']['code'] < 2000: # task failed
            print("failed")
            return None
        now_time = time.time()
        if now_time - start_time > 300: # wait time exceeds 300s
            print('wait time exceeds 300s')
            return None


if __name__ == '__main__':
    file_recognize('https://float-avatar-audio.oss-cn-shenzhen.aliyuncs.com/test_query.wav')