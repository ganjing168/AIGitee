# 火山引擎人脸融合服务说明

## 📋 服务概述

本项目提供了一个基于Flask的微服务，封装了火山引擎视觉API的人脸融合功能。通过这个服务，您可以方便地调用火山引擎的人脸融合能力，将源图像中的人脸融合到模板图像中。

## 🛠️ 文件结构

当前目录包含以下主要文件：

- `volcengine_face_swap_service.py` - Flask微服务主程序，提供人脸融合API接口
- `call_face_swap_api.py` - 调用人脸融合API的客户端脚本
- `requirements.txt` - 项目依赖列表
- `README_人脸融合服务说明.md` - 本使用指南

## 🚀 快速开始

### 步骤1：安装依赖

首先，安装项目所需的所有依赖包：

```bash
pip install -r requirements.txt
```

### 步骤2：启动Flask服务

在第一个终端窗口中启动人脸融合服务：

```bash
python volcengine_face_swap_service.py
```

服务启动后，将在 `http://localhost:5001` 上运行。您将看到类似以下的输出：

```
正在启动火山引擎人脸融合服务...
服务地址: http://0.0.0.0:5001
API超时设置: 120秒
 * Serving Flask app 'volcengine_face_swap_service'
 * Debug mode: on
...
```

### 步骤3：使用客户端脚本调用API

在第二个终端窗口中运行客户端脚本：

```bash
python call_face_swap_api.py
```

脚本将自动连接到Flask服务，并发送人脸融合请求。

## 📡 API端点说明

Flask服务提供以下API端点：

### 1. `/` - 首页

**方法**: GET

显示服务运行状态。

### 2. `/health` - 健康检查接口

**方法**: GET

用于检查服务是否正常运行。

**成功响应**:
```json
{
  "status": "healthy",
  "version": "1.1",
  "message": "Flask server is running",
  "features": ["两张图片融合", "三张图片融合"]
}
```

### 3. `/api/face-swap` - 人脸融合接口

**方法**: POST

**请求参数** (JSON格式):
- `access_key`: 火山引擎访问密钥
- `secret_key`: 火山引擎密钥
- `source_image_url`: 源图像URL（包含人脸的图像）
- `template_image_url`: 模板图像URL（要融合的目标图像）
- `source_image_url2`: （可选）第二张源图像URL
- `multi_image_mode`: （可选）是否启用多图模式，默认为false

**示例请求** (两张图片):
```json
{
  "access_key": "YOUR_ACCESS_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "source_image_url": "https://example.com/source.jpg",
  "template_image_url": "https://example.com/template.jpg"
}
```

**示例请求** (三张图片):
```json
{
  "access_key": "YOUR_ACCESS_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "source_image_url": "https://example.com/source1.jpg",
  "template_image_url": "https://example.com/template.jpg",
  "source_image_url2": "https://example.com/source2.jpg",
  "multi_image_mode": true
}
```

**成功响应**:
```json
{
  "success": true,
  "result": {"data": {"video_url": "生成的视频URL"}}, 
  "elapsed_time": 10.5
}
```

**失败响应**:
```json
{
  "success": false,
  "error": "错误信息"
}
```

## ⚙️ 配置说明

### 修改超时设置

在 `volcengine_face_swap_service.py` 文件中，修改API请求超时：

```python
# 设置API超时时间(秒)
API_TIMEOUT = 120
```

在 `call_face_swap_api.py` 文件中，修改客户端请求超时（应大于服务端超时）：

```python
# 设置超时时间(秒) - 应大于服务端的API_TIMEOUT设置
CLIENT_TIMEOUT = 180  # 3分钟超时
```

### 修改请求参数

在 `call_face_swap_api.py` 文件中，您可以修改默认的请求参数：

**两张图片模式**:
```python
request_data = {
    "access_key": "YOUR_ACCESS_KEY",
    "secret_key": "YOUR_SECRET_KEY",
    "source_image_url": "https://example.com/source.jpg",
    "template_image_url": "https://example.com/template.jpg"
}
```

**三张图片模式**:
```python
request_data = {
    "access_key": "YOUR_ACCESS_KEY",
    "secret_key": "YOUR_SECRET_KEY",
    "source_image_url": "https://example.com/source1.jpg",
    "template_image_url": "https://example.com/template.jpg",
    "source_image_url2": "https://example.com/source2.jpg",
    "multi_image_mode": True
}
```

## 🔍 问题排查

### 常见错误及解决方案

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 无法连接到Flask服务 | 服务未启动或端口被占用 | 确认服务已启动，检查5001端口是否被占用 |
| 请求超时 | 服务器处理时间过长或网络问题 | 检查网络连接，增加脚本中的超时时间 |
| 缺少必要参数 | 请求参数不完整 | 检查是否提供了所有必要参数 |
| API调用失败 | 火山引擎API配置问题 | 检查access_key和secret_key是否正确 |

## ❗ 注意事项

- 本服务使用火山引擎视觉API，需要有效的access_key和secret_key
- 默认超时时间为120秒（服务端）和180秒（客户端）
- 请确保您有处理和编辑相关图像的合法权利
- 服务运行期间，请保持网络连接畅通
- 生成的视频URL可能有有效期限制，请及时使用

---

文档更新时间：2024-01-01