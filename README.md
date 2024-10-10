## 运行

### step1
安装intel gpu驱动，以添加对*ollama*的支持。参考https://github.com/intel-analytics/ipex-llm/blob/main/docs/mddocs/Quickstart/ollama_quickstart.md

完成ollama的安装后通过命令

```
conda activate llm-cpp
init-ollama
```

和
```
export OLLAMA_NUM_GPU=999
export no_proxy=localhost,127.0.0.1
export ZES_ENABLE_SYSMAN=1
source /opt/intel/oneapi/setvars.sh
export SYCL_CACHE_PERSISTENT=1
# [optional] under most circumstances, the following environment variable may improve performance, but sometimes this may also cause performance degradation
export SYCL_PI_LEVEL_ZERO_USE_IMMEDIATE_COMMANDLISTS=1
# [optional] if you want to run on single GPU, use below command to limit GPU may improve performance
export ONEAPI_DEVICE_SELECTOR=level_zero:0

./ollama serve
```


完成ollama的启动。可以新开一个终端输入ollama list检查ollama是否安装成功，同时可以看到原启动ollama的日志页面有日志输出。如果顺利将会看到类似如下的输出。这里检测到的设备是A770。
```
found 1 SYCL devices:
|  |                   |                                       |       |Max    |        |Max  |Global |                     |
|  |                   |                                       |       |compute|Max work|sub  |mem    |                     |
|ID|        Device Type|                                   Name|Version|units  |group   |group|size   |       Driver version|
|--|-------------------|---------------------------------------|-------|-------|--------|-----|-------|---------------------|
| 0| [level_zero:gpu:0]|                Intel Arc A770 Graphics|    1.3|    512|    1024|   32| 16225M|            1.3.29735|
```
### step2
安装chatchat

参考

https://github.com/chatchat-space/Langchain-Chatchat/blob/master/README.md#%E6%BA%90%E7%A0%81%E5%AE%89%E8%A3%85%E9%83%A8%E7%BD%B2%E5%BC%80%E5%8F%91%E9%83%A8%E7%BD%B2


完成安装即可。注意要正确指定目录！
使用下面的命令启动即可
>chatchat start -a

挂起启动命令：(日志文件保存在当前目录的output.log)
```
nohup npm run dev > output.log 2>&1 & 
```

### step3
启动后端服务
进入/Chatbot目录下执行./run.sh


### step4
启动前端服务
进入/chatbot-front目录下执行npm run dev


### 注意事项

启用浏览器对asr和tts的支持，在浏览器中输入：

chrome://flags/#unsafely-treat-insecure-origin-as-secure

填写域名或IP并选择Enabled/启用，重启浏览器，在进入服务页面录音时点击允许录音即可。
