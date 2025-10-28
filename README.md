# Coze 工作流 API 调用工具

一个用于调用 Coze 平台工作流 API 的 Python 工具集，支持同步和异步两种执行模式，提供完整的调用、轮询和结果保存功能。

---

## 📋 项目简介

本项目提供了便捷的 Python 脚本来调用 Coze 平台的工作流 API，包括：

- **同步执行**：适用于执行时间较短的工作流（建议不超过 5 分钟）
- **异步执行**：适用于执行时间较长的工作流，支持自动轮询获取结果
- **结果保存**：自动将输入参数和执行结果保存为 JSON 文件，便于后续分析和追溯

---

## ✨ 功能特性

- ✅ **双模式执行**：支持同步和异步两种执行模式
- ✅ **自动轮询**：异步模式支持指数退避策略的智能轮询
- ✅ **完整记录**：保存包含输入参数和执行结果的完整 JSON 文件
- ✅ **错误处理**：完善的异常处理和错误提示
- ✅ **友好输出**：清晰的控制台输出，实时显示执行状态
- ✅ **配置简单**：所有配置集中在脚本顶部，便于修改

---

## 📁 项目结构

```
cozeapi/
├── README.md                          # 项目说明文档（本文件）
├── README_脚本使用说明.md             # 详细脚本使用说明
├── Coze工作流API调用说明.md           # Coze API 详细文档
├── requirements.txt                   # Python 依赖包
├── workflow_sync.py                   # 同步执行脚本
└── workflow_async.py                  # 异步执行与轮询脚本
```

### 文件说明

| 文件 | 说明 |
|------|------|
| `README.md` | 项目主文档，提供项目概览和快速开始指南 |
| `README_脚本使用说明.md` | 详细的脚本使用说明和配置指南 |
| `Coze工作流API调用说明.md` | 基于 Coze 官方文档整理的完整 API 规范 |
| `requirements.txt` | Python 依赖包列表 |
| `workflow_sync.py` | 同步执行工作流的脚本 |
| `workflow_async.py` | 异步执行工作流并自动轮询结果的脚本 |

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.6 或更高版本
- 有效的 Coze 平台账号和 Access Token
- 已创建的工作流 ID

### 2. 安装依赖

```bash
# 克隆或下载项目后，安装依赖包
pip install -r requirements.txt
```

或者直接安装：

```bash
pip install requests
```

### 3. 配置脚本

#### 同步执行脚本配置

打开 `workflow_sync.py`，在文件顶部修改配置：

```python
YOUR_ACCESS_TOKEN = "your_access_token_here"  # 替换为您的 Access Token
WORKFLOW_ID = "your_workflow_id_here"         # 替换为您的工作流 ID

INPUTS = {
    "param1": "value1",  # 根据实际工作流需求修改
    "param2": "value2"
}
```

#### 异步执行脚本配置

打开 `workflow_async.py`，进行同样的配置，还可以调整轮询参数：

```python
YOUR_ACCESS_TOKEN = "your_access_token_here"
WORKFLOW_ID = "your_workflow_id_here"
INPUTS = {
    "param1": "value1",
    "param2": "value2"
}

# 轮询配置（可选）
INITIAL_POLL_INTERVAL = 2    # 初始轮询间隔（秒）
MAX_POLL_INTERVAL = 30       # 最大轮询间隔（秒）
MAX_POLL_ATTEMPTS = 120      # 最大轮询次数
```

### 4. 运行脚本

#### 同步执行

```bash
python workflow_sync.py
```

#### 异步执行

```bash
python workflow_async.py
```

---

## 📖 详细使用指南

### 同步执行模式

**适用场景**：
- 工作流执行时间较短（建议不超过 5 分钟）
- 需要立即获取执行结果
- 适合快速测试和验证

**执行流程**：
1. 发送同步执行请求
2. 等待工作流执行完成
3. 返回完整结果
4. 自动保存到 JSON 文件

**示例输出**：
```
============================================================
Coze 工作流同步执行
============================================================
工作流 ID: your_workflow_id
输入参数: {
  "param1": "value1",
  "param2": "value2"
}
------------------------------------------------------------
正在发送请求...

请求成功！
============================================================
响应结果:
{
  "run_id": "run123",
  "status": "completed",
  "output": { ... }
}
============================================================

结果已保存到文件: run123_20251028T155840.json
```

### 异步执行模式

**适用场景**：
- 工作流执行时间较长
- 需要异步处理，不阻塞主程序
- 适合生产环境使用

**执行流程**：
1. 发送异步执行请求，获取 `run_id`
2. 自动轮询任务状态（指数退避策略）
3. 任务完成后获取最终结果
4. 自动保存到 JSON 文件

**轮询策略**：
- 初始间隔：2 秒
- 最大间隔：30 秒（指数退避）
- 自动判断任务状态，完成后停止轮询

---

## 📄 输出文件格式

两个脚本都会自动将结果保存为 JSON 文件，文件命名规则：

**格式**：`{run_id}_{created_at}.json`

**示例**：`run123_20251028T155840.json`

**JSON 结构**：
```json
{
  "inputs": {
    "param1": "value1",
    "param2": "value2"
  },
  "response": {
    "run_id": "run123",
    "workflow_id": "your_workflow_id",
    "status": "completed",
    "inputs": { ... },
    "outputs": { ... },
    "created_at": "2025-10-28T15:58:40Z",
    "updated_at": "2025-10-28T16:00:00Z"
  }
}
```

**字段说明**：
- `inputs`：本次运行的工作流输入参数
- `response`：工作流 API 返回的完整响应数据

---

## 🔧 配置说明

### 必需配置

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `YOUR_ACCESS_TOKEN` | Coze API 访问令牌 | 通过 Coze 平台的 OAuth 机制获取 |
| `WORKFLOW_ID` | 工作流唯一标识符 | 在 Coze 平台创建工作流后获取 |
| `INPUTS` | 工作流输入参数 | 根据工作流定义配置 |

### 可选配置（异步脚本）

| 配置项 | 默认值 | 说明 |
|-------|--------|------|
| `INITIAL_POLL_INTERVAL` | 2 秒 | 初始轮询间隔 |
| `MAX_POLL_INTERVAL` | 30 秒 | 最大轮询间隔 |
| `MAX_POLL_ATTEMPTS` | 120 次 | 最大轮询次数 |

---

## 📚 API 文档

详细的 API 规范和使用说明，请参考：

- [Coze工作流API调用说明.md](./Coze工作流API调用说明.md) - 完整的 API 文档
- [README_脚本使用说明.md](./README_脚本使用说明.md) - 脚本使用详细说明

**API 端点**：
- 工作流执行：`POST https://api.coze.cn/v1/workflow/run`
- 历史查询：`GET https://api.coze.cn/v1/workflow/history/{run_id}`

---

## ⚠️ 注意事项

### 1. 安全性

- **Token 保护**：请妥善保管您的 Access Token，不要提交到版本控制系统
- 建议使用环境变量或配置文件管理敏感信息（生产环境）

### 2. 超时设置

- 同步脚本默认超时为 5 分钟（300 秒）
- 长时间运行的工作流建议使用异步模式
- 可根据需要调整 `timeout` 参数

### 3. 输入参数

- 确保 `INPUTS` 中的参数名称与工作流定义中的输入参数名称完全一致
- 注意参数类型匹配（字符串、数字、对象等）

### 4. 轮询策略

- 异步脚本使用指数退避策略，避免频繁请求
- 可根据实际情况调整轮询间隔和最大次数

### 5. 错误处理

- 脚本已包含完善的错误处理机制
- 建议在生产环境中增加日志记录功能

---

## ❓ 常见问题

### Q1: 如何获取 Access Token？

A: 通过 Coze 平台的 OAuth 机制获取。具体方法请参考 [Coze 官方文档](https://www.coze.cn/open/docs)。

### Q2: 如何获取 Workflow ID？

A: 在 Coze 平台创建工作流后，可以在工作流详情页面找到 ID。

### Q3: 同步执行超时怎么办？

A: 可以修改脚本中的 `timeout` 参数，或者改用异步执行模式。

### Q4: 异步任务一直处于 pending 状态？

A: 检查工作流配置是否正确，或增加 `MAX_POLL_ATTEMPTS` 的值。

### Q5: 输入参数不匹配？

A: 确保参数名称与工作流定义中的输入参数名称完全一致，注意大小写。

### Q6: JSON 文件保存在哪里？

A: 保存在脚本运行时的当前目录下。

---

## 🔗 相关链接

- [Coze 开放平台](https://www.coze.cn/open)
- [Coze API 文档](https://www.coze.cn/open/docs)
- [工作流执行 API](https://www.coze.cn/open/docs/developer_guides/workflow_run)
- [工作流历史查询 API](https://www.coze.cn/open/docs/developer_guides/workflow_history)

---

## 📝 更新日志

### v1.0 (2025-01-28)

- ✨ 初始版本发布
- ✅ 支持同步执行模式
- ✅ 支持异步执行与自动轮询
- ✅ 自动保存输入参数和执行结果
- ✅ 完善的错误处理机制

---

## 📄 许可证

本项目仅供学习和开发使用。

---

## 💡 贡献

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

**祝使用愉快！** 🎉

