#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coze 工作流同步执行脚本
基于 Coze 官方 API 文档编写
"""

import requests
import json
import os
from datetime import datetime
from typing import Dict, Any


# ==================== 配置区域 ====================
# 请在此处填写您的配置信息

YOUR_ACCESS_TOKEN = "your_access_token_here"  # 请替换为您的 Access Token
WORKFLOW_ID = "your_workflow_id_here"  # 请替换为您的工作流 ID

# 工作流输入参数（根据实际工作流需求修改）
INPUTS = {
    "param1": "value1",
    "param2": "value2"
}
# ==================== 配置区域结束 ====================


# API 端点
WORKFLOW_RUN_URL = "https://api.coze.cn/v1/workflow/run"


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


def execute_workflow_sync() -> None:
    """
    同步执行工作流
    """
    print("=" * 60)
    print("Coze 工作流同步执行")
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
        "async": False  # 同步执行
    }
    
    try:
        print("正在发送请求...")
        response = requests.post(
            WORKFLOW_RUN_URL,
            headers=headers,
            json=payload,
            timeout=300  # 5分钟超时
        )
        
        # 检查 HTTP 状态码
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        print("\n请求成功！")
        print("=" * 60)
        print("响应结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("=" * 60)
        
        # 保存到 JSON 文件
        run_id = result.get("run_id", "unknown")
        created_at = result.get("created_at", datetime.utcnow().isoformat() + "Z")
        
        filename = save_result_to_json(result, INPUTS, run_id, created_at)
        print(f"\n结果已保存到文件: {filename}")
        
        # 打印状态信息
        status = result.get("status", "unknown")
        print(f"\n执行状态: {status}")
        
        if status == "completed":
            output = result.get("output", {})
            if output:
                print(f"输出结果: {json.dumps(output, ensure_ascii=False, indent=2)}")
        elif status == "failed":
            error = result.get("error", {})
            if error:
                print(f"错误信息: {json.dumps(error, ensure_ascii=False, indent=2)}")
        
    except requests.exceptions.HTTPError as e:
        print(f"\nHTTP 错误: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
            except:
                print(f"响应内容: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\n请求异常: {e}")
    except json.JSONDecodeError as e:
        print(f"\nJSON 解析错误: {e}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"\n发生未知错误: {e}")


if __name__ == "__main__":
    # 检查配置
    if YOUR_ACCESS_TOKEN == "your_access_token_here":
        print("⚠️  警告: 请先配置 YOUR_ACCESS_TOKEN")
    if WORKFLOW_ID == "your_workflow_id_here":
        print("⚠️  警告: 请先配置 WORKFLOW_ID")
    
    execute_workflow_sync()

