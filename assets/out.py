#!/usr/bin/python
import json
import sys
import requests
import time
import os


def get_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def get_env():
    BUILD_PIPELINE_NAME = os.getenv('BUILD_PIPELINE_NAME')
    BUILD_PIPELINE_ID = os.getenv('BUILD_PIPELINE_ID')
    BUILD_NAME = os.getenv('BUILD_NAME')
    BUILD_TEAM_NAME = os.getenv('BUILD_TEAM_NAME')
    BUILD_JOB_NAME = os.getenv('BUILD_JOB_NAME')
    BUILD_ID = os.getenv('BUILD_ID')
    BUILD_TEAM_ID = os.getenv('BUILD_TEAM_ID')
    BUILD_JOB_ID = os.getenv('BUILD_JOB_ID')
    ATC_EXTERNAL_URL = os.getenv('ATC_EXTERNAL_URL')
    URL = '{ATC_EXTERNAL_URL}/teams/{BUILD_TEAM_NAME}/pipelines/{BUILD_PIPELINE_NAME}/jobs/{BUILD_JOB_NAME}/builds/{BUILD_NAME}'.format(
        ATC_EXTERNAL_URL=ATC_EXTERNAL_URL,
        BUILD_TEAM_NAME=BUILD_TEAM_NAME,
        BUILD_PIPELINE_NAME=BUILD_PIPELINE_NAME,
        BUILD_JOB_NAME=BUILD_JOB_NAME,
        BUILD_NAME=BUILD_NAME)
    env_dict = {
        'BUILD_PIPELINE_NAME': BUILD_PIPELINE_NAME,
        'BUILD_PIPELINE_ID': BUILD_PIPELINE_ID,
        'BUILD_NAME': BUILD_NAME,
        'BUILD_TEAM_NAME': BUILD_TEAM_NAME,
        'BUILD_JOB_NAME': BUILD_JOB_NAME,
        'BUILD_ID': BUILD_ID,
        'BUILD_TEAM_ID': BUILD_TEAM_ID,
        'BUILD_JOB_ID': BUILD_JOB_ID,
        'ATC_EXTERNAL_URL': ATC_EXTERNAL_URL,
        'URL': URL
    }
    return env_dict


def get_args(stream):
    payload = json.load(stream)
    return payload


def payload_data(payload):
    source = payload["params"]
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send" if not source.get("url") else source.get("url")
    secret = source["secret"]
    msgtype = "markdown" if not source.get("msgtype") else source.get("msgtype")
    # success, failed, abort, error
    level = "success" if not source.get("level") else source.get("level")
    content = "No content" if not source.get("content") else source.get("content")
    payload_dict = {"url": url, "secret": secret, "msgtype": msgtype, "level": level,
                    "content": content}
    return payload_dict


def get_title_info(level):
    title_info = ""
    level = level.lower()
    if level == "success":
        title_info = "<font color=\"info\">Job Success</font>"
    elif level == "failed":
        title_info = "<font color=\"warning\">Job Failed</font>"
    elif level == "abort":
        title_info = "<font color=\"comment\">Job Abort</font>"
    elif level == 'error':
        title_info = "<font color=\"warning\">Job Error</font>"
    return title_info


def message(msgtype, level, content):
    BUILD_PIPELINE_NAME, BUILD_PIPELINE_ID, BUILD_NAME, BUILD_TEAM_NAME, BUILD_JOB_NAME, BUILD_ID, BUILD_TEAM_ID, BUILD_JOB_ID, ATC_EXTERNAL_URL, URL = get_env().values()
    message = {
        "msgtype": msgtype,
        "markdown": {
            "content": ""
        }
    }

    base_content_info = '''
>**Event Details**
>TIME: <font color=\"comment\">{time}</font>
>PIPELINE_NAME: <font color=\"info\">{BUILD_PIPELINE_NAME}</font>
>CONTENT: <font color=\"info\">{content}</font>
>TEAM_NAME: <font color=\"comment\">{BUILD_TEAM_NAME}</font>
>JOB_NAME: <font color=\"comment\">{BUILD_JOB_NAME}</font>
>BUILD_NAME: <font color=\"comment\">{BUILD_NAME}</font>
>For more details, click: [Event]({URL})
'''.format(time=get_time(), BUILD_TEAM_NAME=BUILD_TEAM_NAME, BUILD_PIPELINE_NAME=BUILD_PIPELINE_NAME,
           BUILD_JOB_NAME=BUILD_JOB_NAME, BUILD_NAME=BUILD_NAME, URL=URL, content=content)
    content = base_content_info

    message.get("markdown")["content"] = get_title_info(level) + "\n" + content

    return message


def post_message(url, secret, data):
    headers = {
        'Content-Type': 'text/plain'
    }

    params = {
        "key": secret
    }
    data = json.dumps(data)
    response = requests.request("POST", url, headers=headers, data=data, params=params)
    if response.status_code != 200:
        print(response.json())


def get_timestamp():
    return str(int(time.time()))


def _out(stream):
    payload = get_args(stream)
    payload_dict = payload_data(payload)

    url, secret, msgtype, level, content = payload_dict.values()

    data = message(msgtype, level, content)
    post_message(url, secret, data)
    timestamp = get_timestamp()
    BUILD_PIPELINE_NAME, BUILD_PIPELINE_ID, BUILD_NAME, BUILD_TEAM_NAME, BUILD_JOB_NAME, BUILD_ID, BUILD_TEAM_ID, BUILD_JOB_ID, ATC_EXTERNAL_URL, _ = get_env().values()
    return {
        "version": {"version": timestamp},
        "metadata": [
            {"BUILD_PIPELINE_NAME": BUILD_PIPELINE_NAME},
            {"BUILD_PIPELINE_ID": BUILD_PIPELINE_ID},
            {"BUILD_NAME": BUILD_NAME},
            {"BUILD_TEAM_NAME": BUILD_TEAM_NAME},
            {"BUILD_JOB_NAME": BUILD_JOB_NAME},
            {"BUILD_ID": BUILD_ID},
            {"BUILD_TEAM_ID": BUILD_TEAM_ID},
            {"BUILD_JOB_ID": BUILD_JOB_ID},
            {"ATC_EXTERNAL_URL": ATC_EXTERNAL_URL},
        ]
    }

if __name__ == "__main__":
    print(json.dumps(_out(sys.stdin)))
