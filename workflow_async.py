#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coze 工作流异步执行与轮询脚本
基于 Coze 官方 API 文档编写
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional


# ==================== 配置区域 ====================
# 请在此处填写您的配置信息

YOUR_ACCESS_TOKEN = "your_access_token_here"  # 请替换为您的 Access Token
WORKFLOW_ID = "your_workflow_id_here"  # 请替换为您的工作流 ID

# 工作流输入参数（根据实际工作流需求修改）
INPUTS = {
    "param1": "value1",
    "param2": "value2"
}

# 轮询配置
INITIAL_POLL_INTERVAL = 2  # 初始轮询间隔（秒）
MAX_POLL_INTERVAL = 30  # 最大轮询间隔（秒）
MAX_POLL_ATTEMPTS = 120  # 最大轮询次数（如果每次2秒，最多等待4分钟）
# ==================== 配置区域结束 ====================


# API 端点
WORKFLOW_RUN_URL = "https://api.coze.cn/v1/workflow/run"
WORKFLOW_HISTORY_URL = "https://api.coze.cn/v1/workflow/history"


def save_result_to_json(response_data: Dict[Any, Any], inputs: Dict[Any, Any], run_id: str, created_at: str) -> str:
    """
    保存结果到 JSON 文件
    
    Args:
        response_data: 工作流返回的全部内容
        inputs: 工作流输入参数
        run_id: 运行 ID
        created_at: 创建时间
    
    Returns:
        保存的文件路径
    """
    # 处理时间格式，去掉特殊字符用于文件名
    # 将 ISO 8601 格式转换为文件名友好的格式
    # 例如：2025-10-28T15:58:40Z -> 20251028T155840
    time_str = created_at.replace("-", "").replace(":", "").replace("Z", "").replace("T", "T")
    
    # 生成文件名：run_id + created_at
    filename = f"{run_id}_{time_str}.json"
    
    # 确保文件路径安全
    safe_filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', 'T'))
    
    # 构建包含输入参数和返回结果的数据结构
    output_data = {
        "inputs": inputs,  # 本次运行的工作流输入参数
        "response": response_data  # 本次工作流返回的全部内容
    }
    
    # 保存 JSON 文件
    with open(safe_filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return safe_filename


def start_workflow_async() -> Optional[Dict[Any, Any]]:
    """
    启动异步工作流执行
    
    Returns:
        启动响应数据，包含 run_id
    """
    print("=" * 60)
    print("启动 Coze 工作流异步执行")
    print("=" * 60)
    print(f"工作流 ID: {WORKFLOW_ID}")
    print(f"输入参数: {json.dumps(INPUTS, ensure_ascii=False, indent=2)}")
    print("-" * 60)
    
    # 构建请求头
    headers = {
        "Authorization": f"Bearer {YOUR_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 构建请求体
    payload = {
        "workflow_id": WORKFLOW_ID,
        "inputs": INPUTS,
        "async": True  # 异步执行
    }
    
    try:
        print("正在发送异步执行请求...")
        response = requests.post(
            WORKFLOW_RUN_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # 检查 HTTP 状态码
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        print("\n异步任务已启动！")
        print("-" * 60)
        print("启动响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        run_id = result.get("run_id")
        status = result.get("status", "unknown")
        
        print(f"\n任务 ID (run_id): {run_id}")
        print(f"初始状态: {status}")
        print("=" * 60)
        
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP 错误: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
            except:
                print(f"响应内容: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n❌ 请求异常: {e}")
        return None
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")
        return None


def query_workflow_status(run_id: str) -> Optional[Dict[Any, Any]]:
    """
    查询工作流执行状态
    
    Args:
        run_id: 工作流运行的唯一标识符
    
    Returns:
        查询结果
    """
    headers = {
        "Authorization": f"Bearer {YOUR_ACCESS_TOKEN}"
    }
    
    url = f"{WORKFLOW_HISTORY_URL}/{run_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"\n⚠️  查询状态时发生 HTTP 错误: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
            except:
                print(f"响应内容: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n⚠️  查询状态时发生请求异常: {e}")
        return None
    except Exception as e:
        print(f"\n⚠️  查询状态时发生未知错误: {e}")
        return None


def poll_workflow_result(run_id: str) -> Optional[Dict[Any, Any]]:
    """
    轮询工作流执行结果
    
    Args:
        run_id: 工作流运行的唯一标识符
    
    Returns:
        最终执行结果
    """
    print("\n开始轮询任务状态...")
    print("-" * 60)
    
    poll_interval = INITIAL_POLL_INTERVAL
    poll_count = 0
    
    while poll_count < MAX_POLL_ATTEMPTS:
        poll_count += 1
        print(f"\n第 {poll_count} 次查询... (等待 {poll_interval} 秒)")
        
        # 查询状态
        result = query_workflow_status(run_id)
        
        if result is None:
            print("查询失败，等待后重试...")
            time.sleep(poll_interval)
            # 指数退避
            poll_interval = min(poll_interval * 2, MAX_POLL_INTERVAL)
            continue
        
        status = result.get("status", "unknown")
        print(f"当前状态: {status}")
        
        # 显示简要信息
        if "updated_at" in result:
            print(f"更新时间: {result.get('updated_at')}")
        
        # 检查是否完成
        if status in ["completed", "failed"]:
            print("\n任务执行完成！")
            print("=" * 60)
            return result
        
        # 继续等待
        if status == "pending":
            print("任务等待执行中...")
        elif status == "running":
            print("任务正在执行中...")
        else:
            print(f"任务状态: {status}")
        
        # 等待后继续轮询
        time.sleep(poll_interval)
        
        # 指数退避策略：逐渐增加轮询间隔，但不超过最大值
        if poll_interval < MAX_POLL_INTERVAL:
            poll_interval = min(poll_interval * 1.5, MAX_POLL_INTERVAL)
    
    print(f"\n⚠️  已达到最大轮询次数 ({MAX_POLL_ATTEMPTS})，停止轮询")
    # 最后一次查询获取最新状态
    final_result = query_workflow_status(run_id)
    return final_result


def execute_workflow_async() -> None:
    """
    异步执行工作流并轮询结果
    """
    # 1. 启动异步任务
    start_result = start_workflow_async()
    
    if start_result is None:
        print("\n❌ 无法启动异步任务，程序退出")
        return
    
    run_id = start_result.get("run_id")
    if not run_id:
        print("\n❌ 未获取到 run_id，程序退出")
        return
    
    # 2. 轮询结果
    final_result = poll_workflow_result(run_id)
    
    if final_result is None:
        print("\n⚠️  无法获取最终结果")
        return
    
    # 3. 显示完整结果
    print("\n" + "=" * 60)
    print("完整执行结果:")
    print("=" * 60)
    print(json.dumps(final_result, ensure_ascii=False, indent=2))
    print("=" * 60)
    
    # 4. 保存结果到文件
    created_at = final_result.get("created_at", datetime.utcnow().isoformat() + "Z")
    filename = save_result_to_json(final_result, INPUTS, run_id, created_at)
    print(f"\n结果已保存到文件: {filename}")
    
    # 5. 打印状态总结
    status = final_result.get("status", "unknown")
    print(f"\n最终状态: {status}")
    
    if status == "completed":
        outputs = final_result.get("outputs", {})
        if outputs:
            print(f"\n输出结果:")
            print(json.dumps(outputs, ensure_ascii=False, indent=2))
        else:
            print("\n(无输出结果)")
    elif status == "failed":
        error = final_result.get("error", {})
        if error:
            print(f"\n错误信息:")
            print(json.dumps(error, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    # 检查配置
    if YOUR_ACCESS_TOKEN == "your_access_token_here":
        print("⚠️  警告: 请先配置 YOUR_ACCESS_TOKEN")
    if WORKFLOW_ID == "your_workflow_id_here":
        print("⚠️  警告: 请先配置 WORKFLOW_ID")
    
    execute_workflow_async()

