import json
import requests
import sys
import time

# 设置中文显示
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Flask服务地址
FLASK_SERVICE_URL = "http://localhost:5001/api/face-swap"
HEALTH_CHECK_URL = "http://localhost:5001/health"

# 设置超时时间(秒)
CLIENT_TIMEOUT = 180  # 3分钟超时

def check_service_status():
    """检查Flask服务是否正常运行"""
    try:
        print("正在检查服务状态...")
        response = requests.get(HEALTH_CHECK_URL, timeout=5)
        if response.status_code == 200:
            try:
                health_data = response.json()
                print(f"✅ 服务状态正常: {health_data.get('status')}")
                print(f"版本信息: {health_data.get('version')}")
                return True
            except json.JSONDecodeError:
                print("✅ 服务已启动，但返回数据格式异常")
                return True
        else:
            print(f"❌ 服务返回非200状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到服务: {HEALTH_CHECK_URL}")
        print("请确保Flask服务已启动，命令: python volcengine_face_swap_service.py")
        return False
    except requests.exceptions.Timeout:
        print("❌ 服务连接超时")
        return False
    except Exception as e:
        print(f"❌ 检查服务状态时出错: {str(e)}")
        return False

def call_face_swap_api():
    """调用人脸融合API"""
    # 检查服务状态
    if not check_service_status():
        print("服务未正常运行，无法发送请求")
        return
    
    # 三张测试图片URL
    SOURCE_IMAGE_URL = "https://p26-bot-workflow-sign.byteimg.com/tos-cn-i-mdko3gqilj/2ee4602f2de844749f87b1da6480ad0c.png~tplv-mdko3gqilj-image.image?rk3s=81d4c505&x-expires=1790073184&x-signature=cD3j2d6Bn%2BM8OmztYf2tbaTBuIY%3D"  # 要融合的人脸图片
    TEMPLATE_IMAGE_URL = "https://p26-bot-workflow-sign.byteimg.com/tos-cn-i-mdko3gqilj/2bbbc637223843c990bac55b50253dd8.jpg~tplv-mdko3gqilj-image.image?rk3s=81d4c505&x-expires=1790073171&x-signature=Q2sbn3Jlrnz34wTZx9lq1dl6Uk0%3D"  # 被融合的模板图片
    SOURCE_IMAGE_URL2 = "https://p9-bot-workflow-sign.byteimg.com/tos-cn-i-mdko3gqilj/aac123b8a7bb415dbc2990fa6094c272.jpg~tplv-mdko3gqilj-image.image?rk3s=81d4c505&x-expires=1790077826&x-signature=jvMoEyDVJoyy37dWxvtgQ00xE3g%3D"  # 被融合的模板图片
    
    # 请求参数 - 支持三张图片的融合
    request_data = {
        "access_key": "AKLTMDQ4OTIzYzY0NTk3NDVjNmI3Y2NiNTY2MDNlYWJlZmM",
        "secret_key": "T1RJMFpURXdNR013TVRVeU5EZGxabUV3TkRrM05USmhaalpqWmpoallqTQ==",
        "source_image_url": SOURCE_IMAGE_URL,
        "template_image_url": TEMPLATE_IMAGE_URL,
        "source_image_url2": SOURCE_IMAGE_URL2,
        "multi_image_mode": True  # 启用多图模式
    }
    
    print("\n🚀 准备发送人脸融合请求...")
    print(f"请求URL: {FLASK_SERVICE_URL}")
    print(f"超时设置: {CLIENT_TIMEOUT}秒")
    print("\n📋 请求参数摘要:")
    print(f"- 源图像URL: {SOURCE_IMAGE_URL[:50]}...")
    print(f"- 模板图像URL: {TEMPLATE_IMAGE_URL[:50]}...")
    print(f"- 第二张源图像URL: {SOURCE_IMAGE_URL2[:50]}...")
    print(f"- 多图模式: 已启用")
    
    try:
        # 记录请求开始时间
        start_time = time.time()
        
        # 发送POST请求
        print("\n⏳ 正在发送请求，请稍候...")
        response = requests.post(
            FLASK_SERVICE_URL,
            json=request_data,
            timeout=CLIENT_TIMEOUT
        )
        
        # 计算请求耗时
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ 请求完成，耗时: {elapsed_time:.2f}秒")
        print(f"响应状态码: {response.status_code}")
        
        # 处理响应
        if response.status_code == 200:
            try:
                result = response.json()
                print("\n📊 响应结果:")
                if result.get('success'):
                    print("✅ 人脸融合成功！")
                    print(f"请求耗时: {result.get('elapsed_time', 'N/A')}秒")
                    
                    # 打印结果详情
                    if 'result' in result:
                        api_result = result['result']
                        if 'data' in api_result and 'video_url' in api_result['data']:
                            print(f"\n🔗 生成的视频URL: {api_result['data']['video_url']}")
                            print("\n💡 使用提示:")
                            print("1. 复制上面的URL到浏览器中查看生成的人脸融合视频")
                            print("2. 注意：生成的URL可能有有效期限制")
                            print("3. 如需调整参数，请修改脚本中的相关图片URL变量")
                        else:
                            print("\n📋 API返回详情:")
                            print(json.dumps(api_result, ensure_ascii=False, indent=2))
                    elif 'raw_response' in result:
                        print("\n📋 API原始响应:")
                        print(result['raw_response'])
                else:
                    print(f"❌ 人脸融合失败: {result.get('error', '未知错误')}")
            except json.JSONDecodeError:
                print("❌ 响应格式无效，无法解析为JSON")
                print("原始响应内容:")
                print(response.text)
        elif response.status_code == 504:
            print("❌ 网关超时，服务处理时间过长")
            print("💡 解决建议:")
            print("1. 检查网络连接是否稳定")
            print("2. 尝试增加CLIENT_TIMEOUT的值")
            print("3. 检查服务端日志，查看具体处理情况")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print("响应内容:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        elapsed_time = time.time() - start_time
        print(f"❌ 请求超时，已等待 {elapsed_time:.2f}秒")
        print("💡 解决建议:")
        print("1. 增加CLIENT_TIMEOUT的值")
        print("2. 检查网络连接是否稳定")
        print("3. 确认服务端是否正常运行")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误，无法连接到服务")
        print("💡 解决建议:")
        print("1. 确认Flask服务已启动")
        print("2. 检查服务地址和端口是否正确")
        print("3. 检查网络连接是否正常")
    except Exception as e:
        print(f"❌ 请求过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔚 请求处理完成")

def main():
    """主函数"""
    print("===== 火山引擎人脸融合API调用工具 =====")
    print(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"客户端版本: 1.1 (支持三张图片融合)")
    
    try:
        # 检查依赖
        import requests
        print("✅ 依赖库检查通过")
    except ImportError:
        print("❌ 缺少依赖库，请先安装: pip install requests")
        return
    
    # 调用API
    call_face_swap_api()

if __name__ == "__main__":
    main()