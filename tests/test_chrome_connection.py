#!/usr/bin/env python3
"""
测试Chrome浏览器连接
"""

import socket
import time
import os
import requests
import json

def test_chrome_connection():
    """测试Chrome连接"""
    print("🌐 Chrome浏览器连接测试")
    print("=" * 40)
    
    # 清除代理设置
    proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']
    old_proxies = {}
    for var in proxy_vars:
        if var in os.environ:
            old_proxies[var] = os.environ[var]
            del os.environ[var]
    
    try:
        print("📡 测试TCP连接...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect(("localhost", 9222))
        print("✅ TCP连接成功!")
        sock.close()
        
        print("\n📡 测试HTTP请求...")
        response = requests.get("http://localhost:9222/json/version", timeout=10)
        
        if response.status_code == 200:
            print("✅ HTTP请求成功!")
            data = response.json()
            print(f"   浏览器: {data.get('Browser', 'Unknown')}")
            print(f"   用户代理: {data.get('User-Agent', 'Unknown')}")
            print(f"   协议版本: {data.get('Protocol-Version', 'Unknown')}")
            print(f"   WebKit版本: {data.get('WebKit-Version', 'Unknown')}")
            
            # 测试页面列表
            print(f"\n📡 获取页面列表...")
            response2 = requests.get("http://localhost:9222/json", timeout=10)
            
            if response2.status_code == 200:
                pages = response2.json()
                print(f"✅ 找到 {len(pages)} 个页面:")
                
                for i, page in enumerate(pages):
                    print(f"\n   页面 {i+1}:")
                    print(f"     ID: {page.get('id', 'N/A')}")
                    print(f"     标题: {page.get('title', 'N/A')}")
                    print(f"     URL: {page.get('url', 'N/A')}")
                    print(f"     类型: {page.get('type', 'N/A')}")
                    
                    if 'webSocketDebuggerUrl' in page:
                        ws_url = page['webSocketDebuggerUrl']
                        print(f"     WebSocket: {ws_url}")
                
                return True, pages
            else:
                print(f"❌ 页面列表请求失败: {response2.status_code}")
                return True, []
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False, []
            
    except requests.exceptions.ConnectTimeout:
        print("❌ 连接超时")
        return False, []
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接错误: {e}")
        return False, []
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False, []
    finally:
        # 恢复代理设置
        for var, value in old_proxies.items():
            os.environ[var] = value

def test_raw_socket():
    """测试原始socket连接"""
    print("\n🔌 原始Socket测试")
    print("=" * 40)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        print("📡 连接到 localhost:9222...")
        sock.connect(("localhost", 9222))
        print("✅ TCP连接成功!")
        
        # 发送HTTP请求
        request = "GET /json/version HTTP/1.1\r\nHost: localhost:9222\r\nConnection: close\r\n\r\n"
        print(f"📤 发送请求...")
        
        sock.send(request.encode())
        
        # 接收响应
        response = b""
        start_time = time.time()
        
        while time.time() - start_time < 5:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
                print(f"📥 收到数据: {len(data)} 字节")
            except socket.timeout:
                break
        
        sock.close()
        
        if response:
            response_str = response.decode('utf-8', errors='ignore')
            print(f"✅ 收到响应 ({len(response)} 字节):")
            print("-" * 40)
            print(response_str)
            print("-" * 40)
            
            # 尝试解析JSON
            if '\r\n\r\n' in response_str:
                headers, body = response_str.split('\r\n\r\n', 1)
                if body.strip():
                    try:
                        json_data = json.loads(body)
                        print(f"✅ JSON解析成功:")
                        for key, value in json_data.items():
                            print(f"   {key}: {value}")
                        return True
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON解析失败: {e}")
            
            return True
        else:
            print("❌ 没有收到任何响应")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_playwright_connection():
    """测试Playwright连接"""
    print(f"\n🎭 Playwright连接测试")
    print("=" * 40)
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            try:
                # 连接到CDP
                browser = p.chromium.connect_over_cdp("ws://localhost:9222")
                print("✅ Playwright连接成功!")
                
                # 获取上下文和页面
                contexts = browser.contexts
                print(f"   找到 {len(contexts)} 个浏览器上下文")
                
                if contexts:
                    context = contexts[0]
                    pages = context.pages
                    print(f"   找到 {len(pages)} 个页面")
                    
                    if pages:
                        page = pages[0]
                        title = page.title()
                        url = page.url
                        print(f"   当前页面标题: {title}")
                        print(f"   当前页面URL: {url}")
                        
                        # 尝试导航到Google
                        print(f"\n🧪 测试页面导航...")
                        try:
                            page.goto("https://www.google.com", timeout=10000)
                            new_title = page.title()
                            new_url = page.url
                            print(f"✅ 导航成功!")
                            print(f"   新页面标题: {new_title}")
                            print(f"   新页面URL: {new_url}")
                            
                        except Exception as e:
                            print(f"⚠️ 页面导航失败: {e}")
                
                browser.close()
                return True
                
            except Exception as e:
                print(f"❌ Playwright连接失败: {e}")
                return False
                
    except ImportError:
        print("❌ Playwright未安装")
        return False

def main():
    """主函数"""
    print("🧪 Chrome浏览器连接测试")
    print("=" * 50)
    
    # 测试基本连接
    success, pages = test_chrome_connection()
    
    if success:
        print(f"\n🎉 Chrome HTTP连接成功!")
        
        # 测试原始socket
        socket_success = test_raw_socket()
        
        if socket_success:
            print(f"\n🎉 原始Socket连接也成功!")
            
            # 测试Playwright
            playwright_success = test_playwright_connection()
            
            if playwright_success:
                print(f"\n🎉 所有测试都成功!")
                print(f"💡 Playwright工具现在应该可以正常使用了")
            else:
                print(f"\n⚠️ HTTP和Socket连接成功，但Playwright连接失败")
        else:
            print(f"\n⚠️ HTTP连接成功，但原始Socket连接失败")
    else:
        print(f"\n❌ Chrome连接失败")
        print(f"💡 请检查:")
        print(f"   1. Chrome是否正确启动并启用远程调试")
        print(f"   2. SSH隧道是否正常工作")
        print(f"   3. 防火墙设置")

if __name__ == "__main__":
    main()
