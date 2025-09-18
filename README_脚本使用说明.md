# 图像编辑API调用脚本使用说明

本文件包含如何使用`call_image_edit_api.py`脚本访问Flask图像编辑服务的说明。

## 前置条件

在运行脚本之前，请确保：

1. Flask图像编辑服务正在运行
2. 您已经安装了必要的Python依赖包

## 运行Flask服务

首先，您需要启动Flask图像编辑服务：

```bash
# 安装依赖（如果尚未安装）
pip install -r requirements.txt

# 运行Flask服务
python image_edit_service.py
```

服务启动后，将在 http://localhost:5000 上运行。

## 运行调用脚本

在Flask服务运行的情况下，打开另一个命令行窗口，执行以下命令：

```bash
python call_image_edit_api.py
```

## 脚本功能说明

`call_image_edit_api.py`脚本会：

1. 向本地Flask服务的`/api/edit-image`端点发送POST请求
2. 使用指定的图像URL：`https://gitee.com/realhugh/imgs/raw/master/qwen_edit8.png`
3. 使用指定的提示词：`将图中红色框中的文字改为"殇",只改变框内的画面，框外的画面维持不变`
4. 打印请求和响应的详细信息
5. 如果请求成功，显示生成的图片URL

## 可能的错误及解决方案

- **连接错误**: 如果看到类似"Connection refused"的错误，请检查Flask服务是否正在运行
- **依赖缺失**: 如果看到导入错误，请确保安装了所有依赖：`pip install -r requirements.txt`
- **API返回错误**: 如果API返回错误，请检查响应中的错误信息以获取更多详情

## 注意事项

- 请确保您的网络连接正常，因为服务需要从网络获取图像
- API调用可能需要一定时间完成，请耐心等待
- 如果需要修改图像URL或提示词，可以直接编辑`call_image_edit_api.py`文件中的`payload`变量