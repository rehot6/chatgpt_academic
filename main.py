import os; os.environ['no_proxy'] = '*' # 避免代理网络产生意外污染
import gradio as gr
from request_llm.bridge_chatgpt import predict
from toolbox import format_io, find_free_port, on_file_uploaded, on_report_generated, get_conf, ArgsGeneralWrapper, DummyWith

API_KEY = os.environ.get('MY_API_KEY')
# 建议您复制一个config_private.py放自己的秘密, 如API和代理网址, 避免不小心传github被别人看到
proxies, WEB_PORT, LLM_MODEL, CONCURRENT_COUNT, AUTHENTICATION, CHATBOT_HEIGHT, LAYOUT= \
    get_conf('proxies', 'WEB_PORT', 'LLM_MODEL', 'CONCURRENT_COUNT', 'AUTHENTICATION', 'CHATBOT_HEIGHT', 'LAYOUT')

# 如果WEB_PORT是-1, 则随机选取WEB端口
PORT = find_free_port() if WEB_PORT <= 0 else WEB_PORT
if not AUTHENTICATION: AUTHENTICATION = None

from check_proxy import get_current_version
initial_prompt = "Serve me as a writing and programming assistant."
title_html = f"<h1 align=\"center\">ChatGPT 学术优化 {get_current_version()}</h1>"
description =  """代码开源和更新[地址🚀](https://github.com/binary-husky/chatgpt_academic)，感谢热情的[开发者们❤️](https://github.com/binary-husky/chatgpt_academic/graphs/contributors)"""

# 问询记录, python 版本建议3.9+（越新越好）
import logging
os.makedirs("gpt_log", exist_ok=True)
try:logging.basicConfig(filename="gpt_log/chat_secrets.log", level=logging.INFO, encoding="utf-8")
except:logging.basicConfig(filename="gpt_log/chat_secrets.log", level=logging.INFO)
print("所有问询记录将自动保存在本地目录./gpt_log/chat_secrets.log, 请注意自我隐私保护哦！")

# 一些普通功能模块
from core_functional import get_core_functions
functional = get_core_functions()

# 高级函数插件
from crazy_functional import get_crazy_functions
crazy_fns = get_crazy_functions()

# 处理markdown文本格式的转变
gr.Chatbot.postprocess = format_io

# 做一些外观色彩上的调整
from theme import adjust_theme, advanced_css
set_theme = adjust_theme()

# 代理与自动更新
from check_proxy import check_proxy, auto_update
# proxy_info = check_proxy(proxies)
proxy_info =  f"无代理"


gr_L1 = lambda: gr.Row().style()
gr_L2 = lambda scale: gr.Column(scale=scale)
if LAYOUT == "TOP-DOWN": 
    gr_L1 = lambda: DummyWith()
    gr_L2 = lambda scale: gr.Row()
    CHATBOT_HEIGHT /= 2

cancel_handles = []
with gr.Blocks(title="ChatGPT 学术优化", theme=set_theme, analytics_enabled=False, css=advanced_css) as demo:
    gr.HTML(title_html)
    cookies = gr.State({'api_key': API_KEY, 'llm_model': LLM_MODEL})

def follow_file(filename):
    import time
    # 获取文件大小和最后修改时间
    file_size = os.path.getsize(filename)
    last_modified = os.path.getmtime(filename)
    # 开始追踪文件
    with open(filename, 'r') as f:
        while True:
            # 如果文件已经被截断，则重新开始追踪
            if os.path.getsize(filename) < file_size:
                file_size = 0
                f.seek(0)

            # 读取新添加到文件中的内容
            new_data = f.read()

            # 如果文件发生了变化，则输出相应的信息
            if new_data:
                file_size += len(new_data)
                last_modified = os.path.getmtime(filename)
                print(f"File {filename} has been modified at {last_modified}:")
                print(new_data)

            # 暂停一段时间再继续追踪文件
            time.sleep(1)
# gradio的inbrowser触发不太稳定，回滚代码到原始的浏览器打开函数
def auto_opentab_delay():
    import threading, webbrowser, time
    print(f"如果浏览器没有自动打开，请复制并转到以下URL：")
    print(f"\t（亮色主题）: http://localhost:{PORT}")
    print(f"\t（暗色主题）: http://localhost:{PORT}/?__dark-theme=true")
    def open(): 
        time.sleep(2)       # 打开浏览器
        webbrowser.open_new_tab(f"http://localhost:{PORT}/?__dark-theme=true")
    threading.Thread(target=open, name="open-browser", daemon=True).start()
    threading.Thread(target=auto_update, name="self-upgrade", daemon=True).start()
    threading.Thread(target=follow_file, args=("gpt_log/chat_secrets.log",), name="log", daemon=True).start()
# auto_opentab_delay()
demo.queue(concurrency_count=CONCURRENT_COUNT).launch(server_name="0.0.0.0", server_port=PORT, auth=AUTHENTICATION,debug=True)
