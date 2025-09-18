import requests
import sys
import time

# 确保中文显示正常
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    """调用图像编辑API的简单脚本"""
    print("===== 图像编辑API调用脚本 =====")
    
    # Flask服务的地址
    FLASK_URL = "http://localhost:5000"
    API_ENDPOINT = f"{FLASK_URL}/api/edit-image"
    
    # 设置超时时间(秒) - 应大于服务端的API_TIMEOUT设置
    CLIENT_TIMEOUT = 180  # 3分钟超时
    
    # 检查Flask服务是否正在运行
    try:
        print("\n检查Flask服务状态...")
        health_response = requests.get(f"{FLASK_URL}/health", timeout=5)
        if health_response.status_code == 200:
            try:
                health_data = health_response.json()
                print(f"✅ Flask服务运行正常")
                print(f"服务版本: {health_data.get('version', '未知')}")
                print(f"服务时间戳: {health_data.get('timestamp', '未知')}")
            except:
                print("✅ Flask服务运行正常，但无法解析健康状态数据")
        else:
            print(f"❌ Flask服务状态异常，状态码: {health_response.status_code}")
            print(f"响应内容: {health_response.text}")
            print("请先在另一个终端运行: python image_edit_service.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask服务!")
        print(f"请确认服务已启动，地址为: {FLASK_URL}")
        print("\n启动服务的方法:")
        print("1. 打开一个新的终端窗口")
        print("2. 运行命令: python image_edit_service.py")
        print("3. 等待服务启动完成后再运行本脚本")
        return
    except Exception as e:
        print(f"❌ 服务检查失败: {str(e)}")
        return
    
    # 准备请求参数
    request_data = {
        "image": "https://gitee.com/realhugh/imgs/raw/master/qwen_edit8.png",
        "prompt": "将图中红色框中的文字改为'殇',只改变框内的画面，框外的画面维持不变"
    }
    
    print(f"\n请求地址: {API_ENDPOINT}")
    print(f"图像URL: {request_data['image']}")
    print(f"提示词: {request_data['prompt']}")
    print(f"客户端超时设置: {CLIENT_TIMEOUT}秒")
    
    # 发送请求
    try:
        print("\n正在发送请求，请稍候...")
        print("提示: 图像编辑可能需要较长时间，请耐心等待...")
        start_time = time.time()
        response = requests.post(
            API_ENDPOINT,
            json=request_data,  # 使用json参数自动设置Content-Type并序列化
            timeout=CLIENT_TIMEOUT  # 设置较长的超时时间
        )
        elapsed_time = time.time() - start_time
        
        print(f"请求耗时: {elapsed_time:.2f} 秒")
        print(f"响应状态码: {response.status_code}")
        
        # 处理响应
        if response.status_code == 200:
            try:
                result = response.json()
                print("\n✅ 请求成功!")
                if result.get('success'):
                    media_url = result.get('media_url')
                    print(f"🎉 生成的图片URL: {media_url}")
                    print("\n使用说明:")
                    print(f"1. 复制此URL到浏览器中打开查看结果")
                    print(f"2. 或使用命令下载: curl -o edited_image.png '{media_url}'")
                else:
                    error_msg = result.get('error', '未知错误')
                    print(f"❌ 编辑失败: {error_msg}")
                    if 'details' in result:
                        print(f"失败详情: {result['details']}")
            except ValueError:
                print("✅ 请求成功，但无法解析JSON响应")
                print(f"响应内容: {response.text}")
        elif response.status_code == 504:
            print(f"\n❌ 请求超时 (状态码: {response.status_code})")
            print("服务处理时间过长，可能是因为图像较大或服务器繁忙")
            print("请尝试以下解决方法:")
            print("1. 检查服务端日志，确认API调用状态")
            print("2. 增加服务端和客户端的超时设置")
            print("3. 尝试使用较小的图像")
        else:
            print(f"\n❌ 请求失败 (状态码: {response.status_code})")
            try:
                # 尝试解析错误响应
                error_result = response.json()
                print(f"错误信息: {error_result.get('error', '无错误描述')}")
                if 'details' in error_result:
                    print(f"错误详情: {error_result['details']}")
            except:
                print(f"响应内容: {response.text}")
                
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时")
        print(f"服务器在{CLIENT_TIMEOUT}秒内没有响应")
        print("请检查服务端是否仍在运行，以及网络连接是否正常")
        print("\n解决方法:")
        print("1. 确认服务端日志没有错误")
        print("2. 增加客户端和服务端的超时时间")
        print("3. 检查网络连接稳定性")
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接断开")
        print("服务可能在处理请求过程中意外终止")
        print("请检查服务端终端的错误信息")
    except Exception as e:
        print(f"\n❌ 发生未知错误: {str(e)}")
        print("请检查网络连接和Flask服务状态")
    
    print("\n===== 脚本执行完毕 =====")

if __name__ == "__main__":
    main()