from flask import Flask, request, jsonify
import requests
from requests_toolbelt import MultipartEncoder
import os
import contextlib
import mimetypes
import json
import time

# 创建Flask应用实例
app = Flask(__name__)

# API配置
API_TOKEN = "ZBEDIUV6RWGI3LZJ8SJFWTQEPYE2OGPF2JTTF31A"
API_URL = "https://ai.gitee.com/v1/images/edits"
# 设置API请求超时时间(秒)
API_TIMEOUT = 120

@app.route('/api/edit-image', methods=['POST'])
def edit_image():
    try:
        # 获取请求参数
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        prompt = data.get('prompt')
        image_path = data.get('image')
        
        if not prompt or not image_path:
            return jsonify({'error': 'Prompt and image are required'}), 400
        
        # 准备请求参数
        lora_weights = [
            {
                "url": "https://gitee.com/realhugh/materials/raw/master/Qwen-Image-Edit-Lightning-8steps-V1.0.safetensors",
                "weight": 1
            }
        ]
        
        fields = [
            ("prompt", prompt),
            ("num_inference_steps", "35"),
            ("cfg_scale", "8"),
            ("image", image_path),
            ("model", "Qwen-Image-Edit"),
            ("response_format", "url"),
        ]
        
        headers = {
            "Authorization": f"Bearer {API_TOKEN}"
        }
        
        # 处理图像文件
        with contextlib.ExitStack() as stack:
            filepath = image_path
            name = os.path.basename(filepath)
            
            # 下载图像文件（如果是URL）
            if filepath.startswith(("http://", "https://")):
                try:
                    print(f"正在下载图像: {filepath}")
                    start_time = time.time()
                    image_response = requests.get(filepath, timeout=30)
                    image_response.raise_for_status()
                    elapsed_time = time.time() - start_time
                    print(f"图像下载完成，耗时: {elapsed_time:.2f}秒，大小: {len(image_response.content)}字节")
                    fields.append(("image", (name, image_response.content, image_response.headers.get("Content-Type", "application/octet-stream"))))
                except requests.exceptions.Timeout:
                    return jsonify({
                        'success': False,
                        'error': 'Image download timed out'
                    }), 504
                except requests.exceptions.RequestException as e:
                    return jsonify({
                        'success': False,
                        'error': f'Failed to download image: {str(e)}'
                    }), 500
            else:
                # 注意：在实际生产环境中，需要验证文件路径的安全性
                if not os.path.exists(filepath):
                    return jsonify({'error': 'Image file not found'}), 404
                
                mime_type, _ = mimetypes.guess_type(filepath)
                fields.append(("image", (name, stack.enter_context(open(filepath, "rb")), mime_type or "application/octet-stream")))
            
            # 添加lora_weights
            for item in lora_weights:
                fields.append(("lora_weights", item if isinstance(item, str) else json.dumps(item)))
            
            # 发送请求到API
            print(f"正在发送请求到图像编辑API: {API_URL}")
            print(f"提示词: {prompt}")
            
            try:
                start_time = time.time()
                encoder = MultipartEncoder(fields)
                headers["Content-Type"] = encoder.content_type
                response = requests.post(API_URL, headers=headers, data=encoder, timeout=API_TIMEOUT)
                elapsed_time = time.time() - start_time
                print(f"API请求完成，耗时: {elapsed_time:.2f}秒，状态码: {response.status_code}")
            except requests.exceptions.Timeout:
                return jsonify({
                    'success': False,
                    'error': 'API request timed out',
                    'details': f'The request exceeded the timeout of {API_TIMEOUT} seconds'
                }), 504
            except requests.exceptions.RequestException as e:
                return jsonify({
                    'success': False,
                    'error': f'API request failed: {str(e)}'
                }), 500
        
        # 处理响应
        try:
            result = response.json()
            if response.status_code == 200:
                if 'data' in result and result['data']:
                    return jsonify({
                        'success': True,
                        'media_url': result['data'][0]['url']
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'API returned unexpected response',
                        'details': result
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': f'API returned error status code: {response.status_code}',
                    'details': result
                }), response.status_code
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': 'Failed to parse API response',
                'details': response.text
            }), 500
    
    except Exception as e:
        import traceback
        print(f"发生异常: {str(e)}")
        print(f"堆栈跟踪: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

# 健康检查端点
@app.route('/health', methods=['GET'])
def health_check():
    # 可选：添加更完整的健康检查，例如检查API连接
    try:
        # 简单的自我健康检查
        return jsonify({
            'status': 'healthy',
            'version': '1.1',
            'timestamp': time.time(),
            'api_configured': bool(API_TOKEN and API_URL)
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# 主页端点
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'Image Edit API',
        'version': '1.1',
        'endpoints': {
            '/api/edit-image': 'POST - Edit images using AI',
            '/health': 'GET - Check service health'
        },
        'usage_example': {
            'method': 'POST',
            'url': '/api/edit-image',
            'body': {
                'prompt': 'Your edit prompt',
                'image': 'Path or URL to image'
            }
        }
    })

if __name__ == '__main__':
    # 在开发模式下运行Flask应用
    # 注意：生产环境中应使用WSGI服务器如Gunicorn或uWSGI
    print("正在启动图像编辑服务...")
    print(f"服务地址: http://0.0.0.0:5000")
    print(f"API超时设置: {API_TIMEOUT}秒")
    app.run(debug=True, host='0.0.0.0', port=5000)