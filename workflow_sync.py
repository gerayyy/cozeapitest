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

YOUR_ACCESS_TOKEN = "pat_KU3S9H"  # 请替换为您的 Access Token
WORKFLOW_ID = "756"  # 请替换为您的工作流 ID

# 工作流输入参数（根据实际工作流需求修改）
# 注意：参数名称必须与工作流定义中的输入参数名称一致
PARAMETERS = {
    "input": "nihao"  
}

# 可选参数（根据实际需求设置）
BOT_ID = None  # 可选：需要关联的智能体 ID
APP_ID = None  # 可选：工作流关联的扣子应用 ID
EXT = None  # 可选：额外字段，格式：{"latitude": "39.9042", "longitude": "116.4074", "user_id": "xxx"}
WORKFLOW_VERSION = None  # 可选：工作流版本号（仅资源库工作流有效）
CONNECTOR_ID = None  # 可选：渠道 ID，默认 1024（API 渠道）
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
    # 使用当前北京时间生成文件名，格式：sync_20241018101935
    time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"sync_{time_str}.json"
    
    # 构建包含输入参数和返回结果的数据结构
    output_data = {
        "request": request_config,  # 本次运行的所有输入参数和配置
        "response": response_data  # 本次工作流返回的全部内容
    }
    
    # 保存 JSON 文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    return filename


def execute_workflow_sync() -> None:
    """
    同步执行工作流
    """
    print("=" * 60)
    print("Coze 工作流同步执行")
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
        "workflow_id": WORKFLOW_ID
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
    
    # 保存完整的请求配置（用于结果 JSON）
    request_config = payload.copy()
    
    # 执行请求并保存结果
    result = None
    try:
        print("正在发送请求...")
        # 同步模式超时 10 分钟（600秒）
        response = requests.post(
            WORKFLOW_RUN_URL,
            headers=headers,
            json=payload,
            timeout=600
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
    
    # 保存结果到 JSON 文件
    filename = save_result_to_json(result, request_config)
    print(f"\n结果已保存到文件: {filename}")


if __name__ == "__main__":
    # 检查配置
    warnings = []
    if YOUR_ACCESS_TOKEN == "your_access_token_here":
        warnings.append("[警告] 请先配置 YOUR_ACCESS_TOKEN")
    if WORKFLOW_ID == "your_workflow_id_here":
        warnings.append("[警告] 请先配置 WORKFLOW_ID")
    
    if warnings:
        for warning in warnings:
            print(warning)
        print()
    
    execute_workflow_sync()

