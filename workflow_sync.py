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

# 同步/异步模式（同步脚本默认 false）
IS_ASYNC = False  # true: 异步执行（需要专业版），false: 同步执行（默认）
# ==================== 配置区域结束 ====================


# API 端点
WORKFLOW_RUN_URL = "https://api.coze.cn/v1/workflow/run"


def save_result_to_json(response_data: Dict[Any, Any], request_config: Dict[Any, Any], execute_id: str) -> str:
    """
    保存结果到 JSON 文件
    
    Args:
        response_data: API 返回的全部内容
        request_config: 本次运行的完整请求配置（包括所有输入参数）
        execute_id: 执行 ID（用于文件名）
    
    Returns:
        保存的文件路径
    """
    # 使用当前时间戳生成文件名
    time_str = datetime.now().strftime("%Y%m%dT%H%M%S")
    
    # 生成文件名：execute_id + 时间戳
    if execute_id and execute_id != "unknown":
        filename = f"{execute_id}_{time_str}.json"
    else:
        filename = f"workflow_{time_str}.json"
    
    # 确保文件路径安全
    safe_filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', 'T'))
    
    # 构建包含输入参数和返回结果的数据结构
    output_data = {
        "request": request_config,  # 本次运行的所有输入参数和配置
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
    execution_mode = "异步" if IS_ASYNC else "同步"
    print("=" * 60)
    print(f"Coze 工作流{execution_mode}执行")
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
        "is_async": IS_ASYNC
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
    
    try:
        print("正在发送请求...")
        # 同步模式超时 10 分钟（600秒），异步模式只需等待返回 execute_id，30秒足够
        timeout = 600 if not IS_ASYNC else 30
        response = requests.post(
            WORKFLOW_RUN_URL,
            headers=headers,
            json=payload,
            timeout=timeout
        )
        
        # 检查 HTTP 状态码
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        # 检查业务状态码（code 字段）
        code = result.get("code", -1)
        msg = result.get("msg", "")
        
        if code != 0:
            print(f"\n[错误] API 调用失败！")
            print("=" * 60)
            print(f"错误码: {code}")
            print(f"错误信息: {msg}")
            if "detail" in result and "logid" in result["detail"]:
                print(f"日志 ID: {result['detail']['logid']}")
            print("=" * 60)
            
            # 即使失败也保存响应
            execute_id = result.get("execute_id", "unknown")
            filename = save_result_to_json(result, request_config, execute_id)
            print(f"\n错误响应已保存到文件: {filename}")
            return
        
        print("\n[成功] 请求成功！")
        print("=" * 60)
        print("响应结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("=" * 60)
        
        # 获取执行 ID（用于文件名）
        execute_id = result.get("execute_id", "unknown")
        debug_url = result.get("debug_url", "")
        
        # 保存到 JSON 文件
        filename = save_result_to_json(result, request_config, execute_id)
        print(f"\n结果已保存到文件: {filename}")
        
        # 打印详细信息
        if debug_url:
            print(f"\n调试链接: {debug_url}")
            print("(调试链接有效期为 7 天)")
        
        # 处理执行结果
        if IS_ASYNC:
            print(f"\n[成功] 异步任务已启动！")
            print(f"执行 ID (execute_id): {execute_id}")
            print("提示: 请使用「查询工作流异步执行结果 API」获取最终执行结果")
        else:
            # 同步模式，解析 data 字段
            data = result.get("data", "")
            if data:
                try:
                    # data 是 JSON 序列化字符串，需要解析
                    parsed_data = json.loads(data)
                    print(f"\n执行结果:")
                    print(json.dumps(parsed_data, ensure_ascii=False, indent=2))
                except json.JSONDecodeError:
                    # 如果 data 不是 JSON，直接输出字符串
                    print(f"\n执行结果 (字符串):")
                    print(data)
            
            # 打印资源使用情况
            usage = result.get("usage", {})
            if usage:
                print(f"\n资源使用情况:")
                print(f"  输入 Token: {usage.get('input_count', 0)}")
                print(f"  输出 Token: {usage.get('output_count', 0)}")
                print(f"  总 Token: {usage.get('token_count', 0)}")
        
        # 打印日志 ID（如果有）
        if "detail" in result and "logid" in result["detail"]:
            print(f"\n日志 ID: {result['detail']['logid']}")
        
    except requests.exceptions.HTTPError as e:
        print(f"\n[错误] HTTP 错误: {e}")
        if e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"错误详情: {json.dumps(error_detail, ensure_ascii=False, indent=2)}")
            except:
                print(f"响应内容: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\n[错误] 请求异常: {e}")
    except json.JSONDecodeError as e:
        print(f"\n[错误] JSON 解析错误: {e}")
        if 'response' in locals():
            print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"\n[错误] 发生未知错误: {e}")
        import traceback
        traceback.print_exc()


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

