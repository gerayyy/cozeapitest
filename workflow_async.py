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
# 注意：参数名称必须与工作流定义中的输入参数名称一致
PARAMETERS = {
    "param1": "value1",
    "param2": "value2"
}

# 可选参数（根据实际需求设置）
BOT_ID = None  # 可选：需要关联的智能体 ID
APP_ID = None  # 可选：工作流关联的扣子应用 ID
EXT = None  # 可选：额外字段，格式：{"latitude": "39.9042", "longitude": "116.4074", "user_id": "xxx"}
WORKFLOW_VERSION = None  # 可选：工作流版本号（仅资源库工作流有效）
CONNECTOR_ID = None  # 可选：渠道 ID，默认 1024（API 渠道）

# 轮询配置
INITIAL_POLL_INTERVAL = 2  # 初始轮询间隔（秒）
MAX_POLL_INTERVAL = 30  # 最大轮询间隔（秒）
MAX_POLL_ATTEMPTS = 120  # 最大轮询次数（如果每次2秒，最多等待4分钟）
# ==================== 配置区域结束 ====================


# API 端点
WORKFLOW_RUN_URL = "https://api.coze.cn/v1/workflow/run"


def save_result_to_json(response_data: Any, request_config: Dict[Any, Any]) -> str:
    """
    保存结果到 JSON 文件
    
    Args:
        response_data: API 返回的全部内容
        request_config: 本次运行的完整请求配置（包括所有输入参数）
    
    Returns:
        保存的文件路径
    """
    # 使用当前北京时间生成文件名，格式：async_20241018101935
    time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"async_{time_str}.json"
    
    # 构建包含输入参数和返回结果的数据结构
    output_data = {
        "request": request_config,  # 本次运行的所有输入参数和配置
        "response": response_data  # 本次工作流返回的全部内容
    }
    
    # 保存 JSON 文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return filename


def start_workflow_async(request_config: Dict[Any, Any]) -> Optional[Dict[Any, Any]]:
    """
    启动异步工作流执行
    
    Args:
        request_config: 完整的请求配置（用于保存结果）
    
    Returns:
        启动响应数据，包含 execute_id
    """
    print("=" * 60)
    print("启动 Coze 工作流异步执行")
    print("=" * 60)
    print(f"工作流 ID: {WORKFLOW_ID}")
    print(f"输入参数: {json.dumps(PARAMETERS, ensure_ascii=False, indent=2)}")
    if BOT_ID:
        print(f"智能体 ID: {BOT_ID}")
    if APP_ID:
        print(f"应用 ID: {APP_ID}")
    print("-" * 60)
    
    # 构建请求头
    headers = {
        "Authorization": f"Bearer {YOUR_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 构建请求体
    payload = {
        "workflow_id": WORKFLOW_ID,
        "is_async": True  # 异步执行
    }
    
    # 添加可选参数
    if PARAMETERS:
        payload["parameters"] = PARAMETERS
    if BOT_ID:
        payload["bot_id"] = BOT_ID
    if APP_ID:
        payload["app_id"] = APP_ID
    if EXT:
        payload["ext"] = EXT
    if WORKFLOW_VERSION:
        payload["workflow_version"] = WORKFLOW_VERSION
    if CONNECTOR_ID:
        payload["connector_id"] = CONNECTOR_ID
    
    # 执行请求
    result = None
    try:
        print("正在发送异步执行请求...")
        response = requests.post(
            WORKFLOW_RUN_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # 尝试解析响应
        try:
            result = response.json()
        except json.JSONDecodeError:
            # 如果无法解析 JSON，保存原始文本
            result = {"raw_response": response.text, "status_code": response.status_code}
    except Exception as e:
        # 发生异常时保存错误信息
        result = {"error": str(e), "error_type": type(e).__name__}
    
    return result


def query_workflow_status(execute_id: str) -> Optional[Dict[Any, Any]]:
    """
    查询工作流执行状态
    
    Args:
        execute_id: 异步执行事件 ID
    
    Returns:
        查询结果（整个响应，包含 code, msg, data 等）
    """
    headers = {
        "Authorization": f"Bearer {YOUR_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 根据文档，URL 格式为：/workflows/:workflow_id/run_histories/:execute_id
    url = f"https://api.coze.cn/v1/workflows/{WORKFLOW_ID}/run_histories/{execute_id}"
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        # 尝试解析响应
        try:
            return response.json()
        except json.JSONDecodeError:
            # 如果无法解析 JSON，保存原始文本
            return {"raw_response": response.text, "status_code": response.status_code}
    except Exception as e:
        # 发生任何异常时返回错误信息
        return {"error": str(e), "error_type": type(e).__name__}


def poll_workflow_result(execute_id: str) -> Optional[Dict[Any, Any]]:
    """
    轮询工作流执行结果
    
    Args:
        execute_id: 异步执行事件 ID
    
    Returns:
        最终执行结果（整个查询响应）
    """
    print("\n开始轮询任务状态...")
    print("-" * 60)
    
    poll_interval = INITIAL_POLL_INTERVAL
    poll_count = 0
    
    while poll_count < MAX_POLL_ATTEMPTS:
        poll_count += 1
        print(f"\n第 {poll_count} 次查询... (等待 {poll_interval} 秒)")
        
        # 查询状态
        result = query_workflow_status(execute_id)
        
        if result is None or "error" in result:
            print("查询失败，等待后重试...")
            time.sleep(poll_interval)
            # 指数退避
            poll_interval = min(poll_interval * 2, MAX_POLL_INTERVAL)
            continue
        
        # 根据文档，返回的 data 是一个数组，仅含一个对象
        data_array = result.get("data", [])
        if not data_array or len(data_array) == 0:
            print("结果数据为空，等待后重试...")
            time.sleep(poll_interval)
            poll_interval = min(poll_interval * 2, MAX_POLL_INTERVAL)
            continue
        
        # 获取第一个（也是唯一的）执行历史对象
        history = data_array[0]
        execute_status = history.get("execute_status", "unknown")
        print(f"当前状态: {execute_status}")
        
        # 检查是否完成（根据文档：Success / Running / Fail）
        if execute_status in ["Success", "Fail"]:
            print("\n任务执行完成！")
            print("=" * 60)
            return result
        
        # 继续等待（Running 状态）
        if execute_status == "Running":
            print("任务正在执行中...")
        else:
            print(f"任务状态: {execute_status}")
        
        # 等待后继续轮询
        time.sleep(poll_interval)
        
        # 指数退避策略：逐渐增加轮询间隔，但不超过最大值
        if poll_interval < MAX_POLL_INTERVAL:
            poll_interval = min(poll_interval * 1.5, MAX_POLL_INTERVAL)
    
    print(f"\n⚠️  已达到最大轮询次数 ({MAX_POLL_ATTEMPTS})，停止轮询")
    # 最后一次查询获取最新状态
    final_result = query_workflow_status(execute_id)
    return final_result


def execute_workflow_async() -> None:
    """
    异步执行工作流并轮询结果
    """
    # 构建完整的请求配置
    request_config = {
        "workflow_id": WORKFLOW_ID,
        "is_async": True
    }
    if PARAMETERS:
        request_config["parameters"] = PARAMETERS
    if BOT_ID:
        request_config["bot_id"] = BOT_ID
    if APP_ID:
        request_config["app_id"] = APP_ID
    if EXT:
        request_config["ext"] = EXT
    if WORKFLOW_VERSION:
        request_config["workflow_version"] = WORKFLOW_VERSION
    if CONNECTOR_ID:
        request_config["connector_id"] = CONNECTOR_ID
    
    # 1. 启动异步任务
    start_result = start_workflow_async(request_config)
    
    if start_result is None:
        print("\n无法启动异步任务")
        return
    
    # 获取 execute_id
    execute_id = start_result.get("execute_id")
    
    if not execute_id:
        # 如果启动失败，直接保存启动响应
        print("\n未获取到 execute_id，保存启动响应")
        filename = save_result_to_json(start_result, request_config)
        print(f"结果已保存到文件: {filename}")
        return
    
    print(f"\n任务 ID (execute_id): {execute_id}")
    print("=" * 60)
    
    # 2. 轮询结果
    final_result = poll_workflow_result(execute_id)
    
    # 3. 保存结果到文件（无论成功失败，都保存原始结果）
    if final_result is not None:
        filename = save_result_to_json(final_result, request_config)
    else:
        # 如果轮询失败，保存启动响应
        filename = save_result_to_json(start_result, request_config)
    
    print(f"\n结果已保存到文件: {filename}")
    print("=" * 60)


if __name__ == "__main__":
    # 检查配置
    if YOUR_ACCESS_TOKEN == "your_access_token_here":
        print("⚠️  警告: 请先配置 YOUR_ACCESS_TOKEN")
    if WORKFLOW_ID == "your_workflow_id_here":
        print("⚠️  警告: 请先配置 WORKFLOW_ID")
    
    execute_workflow_async()

