# 图像编辑Flask微服务

这是一个基于Flask的微服务，用于调用Gitee AI的图像编辑API。

## 功能特性
- 提供RESTful API接口
- 支持图像编辑功能
- 包含健康检查端点

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
python image_edit_service.py
```

服务将在 http://localhost:5000 启动

## API端点

### 主页
GET http://localhost:5000/
- 显示服务信息和使用示例

### 健康检查
GET http://localhost:5000/health
- 检查服务运行状态

### 图像编辑
POST http://localhost:5000/api/edit-image

#### 请求参数
```json
{
  "prompt": "编辑提示词",
  "image": "图像路径或URL"
}
```

#### 响应示例
```json
{
  "success": true,
  "media_url": "https://example.com/edited-image.jpg"
}
```

## 注意事项
- 本服务使用Gitee AI的API，需要有效的API令牌
- 当前配置中的API令牌仅供示例使用
- 在生产环境中，应使用WSGI服务器如Gunicorn或uWSGI运行
- 服务默认在5000端口运行，可以在代码中修改