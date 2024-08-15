## 运行

```bash

cd Chatbot/

Paddle_server port 8090

./build.sh

./run.sh
# 访问服务器ip:8086/static页面以进行交互
```


### 注意事项

若要使用语音输入，应当使浏览器允许http数据传输，在浏览器中输入：

`chrome://flags/#unsafely-treat-insecure-origin-as-secure`

填写域名或IP并选择Enabled/启用，在进入服务页面录音时点击允许录音即可。

