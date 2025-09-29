import json
import sys
import os
import base64
import datetime
import hashlib
import hmac
import requests
from flask import Flask, request, jsonify

# 初始化Flask应用
app = Flask(__name__)

# 设置基本参数
method = 'POST'
host = 'visual.volcengineapi.com'
region = 'cn-north-1'
endpoint = 'https://visual.volcengineapi.com'
service = 'cv'

# 设置API超时时间(秒)
API_TIMEOUT = 120

# 签名相关函数
def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def getSignatureKey(key, dateStamp, regionName, serviceName):
    kDate = sign(key.encode('utf-8'), dateStamp)
    kRegion = sign(kDate, regionName)
    kService = sign(kRegion, serviceName)
    kSigning = sign(kService, 'request')
    return kSigning

def formatQuery(parameters):
    request_parameters_init = ''
    for key in sorted(parameters):
        request_parameters_init += key + '=' + parameters[key] + '&'
    request_parameters = request_parameters_init[:-1]
    return request_parameters

def signV4Request(access_key, secret_key, service, req_query, req_body):
    """生成V4签名并发送请求"""
    if access_key is None or secret_key is None:
        raise ValueError('No access key is available.')

    t = datetime.datetime.utcnow()
    current_date = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope
    canonical_uri = '/'
    canonical_querystring = req_query
    signed_headers = 'content-type;host;x-content-sha256;x-date'
    payload_hash = hashlib.sha256(req_body.encode('utf-8')).hexdigest()
    content_type = 'application/json'
    canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-content-sha256:' + payload_hash + '\n' + 'x-date:' + current_date + '\n'
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    
    algorithm = 'HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'request'
    string_to_sign = algorithm + '\n' + current_date + '\n' + credential_scope + '\n' + hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
    
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
    
    headers = {
        'X-Date': current_date,
        'Authorization': authorization_header,
        'X-Content-Sha256': payload_hash,
        'Content-Type': content_type
    }
    
    # 发送请求
    request_url = endpoint + '?' + canonical_querystring
    
    try:
        print(f'发送请求到: {request_url}')
        r = requests.post(request_url, headers=headers, data=req_body, timeout=API_TIMEOUT)
        # 使用 replace 方法将 & 替换为 &
        resp_str = r.text.replace("\\u0026", "&")
        return {
            'status_code': r.status_code,
            'content': resp_str
        }
    except Exception as err:
        print(f'请求出错: {err}')
        raise

@app.route('/')
def home():
    """首页"""
    return "火山引擎视觉API - 人脸融合服务正在运行中"

@app.route('/health')
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'version': '1.1',  # 更新版本号
        'message': 'Flask server is running',
        'features': ['两张图片融合', '三张图片融合']
    })

@app.route('/api/face-swap', methods=['POST'])
def face_swap():
    """人脸融合API接口"""
    try:
        # 获取请求参数
        data = request.json
        
        # 验证必要参数
        if not data:
            return jsonify({'success': False, 'error': '请求体不能为空'}), 400
        
        # 提取必要参数
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        source_image_url = data.get('source_image_url')
        template_image_url = data.get('template_image_url')
        
        # 验证关键参数
        if not all([access_key, secret_key, source_image_url, template_image_url]):
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
        
        # 检查是否启用多图模式
        multi_image_mode = data.get('multi_image_mode', False)
        source_image_url2 = data.get('source_image_url2')
        
        # 构建请求参数
        query_params = {
            'Action': 'CVProcess',
            'Version': '2022-08-31',
        }
        formatted_query = formatQuery(query_params)
        
        # 构建请求Body - 根据是否启用多图模式调整参数
        if multi_image_mode and source_image_url2:
            print("启用多图模式，处理三张图片的融合请求")
            body_params = {
                "req_key": "face_swap3_6",
                "image_urls": [source_image_url, source_image_url2, template_image_url],
                "face_type": "l2r",
                "return_url": True,
                "merge_infos": [
                   {
                      "location": 1,
                      "template_location": 1
                   },
                   {
                      "location": 1,
                      "template_location": 2
                   }
                ]
            }
        else:
            print("使用默认模式，处理两张图片的融合请求")
            body_params = {
                "req_key": "face_swap3_6",
                "image_urls": [source_image_url, template_image_url],
                "face_type": "l2r",
                "return_url": True,
                "merge_infos": [
                   {
                      "location": 1,
                      "template_location": 1
                   }
                ]
            }
        
        formatted_body = json.dumps(body_params)
        
        # 调用火山引擎API
        start_time = datetime.datetime.now()
        response = signV4Request(access_key, secret_key, service, formatted_query, formatted_body)
        end_time = datetime.datetime.now()
        
        # 计算请求耗时
        elapsed_time = (end_time - start_time).total_seconds()
        print(f'API请求耗时: {elapsed_time:.2f}秒')
        
        # 处理响应
        if response['status_code'] == 200:
            try:
                result = json.loads(response['content'])
                return jsonify({'success': True, 'result': result, 'elapsed_time': elapsed_time})
            except json.JSONDecodeError:
                return jsonify({'success': True, 'raw_response': response['content'], 'elapsed_time': elapsed_time})
        else:
            return jsonify({
                'success': False,
                'error': f'API调用失败',
                'status_code': response['status_code'],
                'response': response['content']
            }), response['status_code']
            
    except Exception as e:
        print(f'处理请求时出错: {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == "__main__":
    # 设置中文显示
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    print("正在启动火山引擎人脸融合服务...")
    print(f"服务地址: http://0.0.0.0:5001")
    print(f"API超时设置: {API_TIMEOUT}秒")
    
    # 启动服务，监听所有接口，端口5001
    app.run(host='0.0.0.0', port=5001, debug=True)