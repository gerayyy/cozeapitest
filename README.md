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

# 工作流输入参数（根据实际工作流需求修改）
PARAMETERS = {
    "param1": "value1",  # 根据实际工作流定义修改参数名称和值
    "param2": "value2"
}

# 可选参数（根据实际需求设置）
BOT_ID = None           # 可选：需要关联的智能体 ID
APP_ID = None           # 可选：工作流关联的扣子应用 ID
EXT = None              # 可选：额外字段，如经纬度、用户ID等
WORKFLOW_VERSION = None # 可选：工作流版本号（仅资源库工作流有效）
CONNECTOR_ID = None     # 可选：渠道 ID，默认 1024（API 渠道）
```

#### 异步执行脚本配置

打开 `workflow_async.py`，进行同样的配置，还可以调整轮询参数：

```python
YOUR_ACCESS_TOKEN = "your_access_token_here"
WORKFLOW_ID = "your_workflow_id_here"

# 工作流输入参数（根据实际工作流需求修改）
PARAMETERS = {
    "param1": "value1",
    "param2": "value2"
}

# 可选参数（根据实际需求设置）
BOT_ID = None
APP_ID = None
EXT = None
WORKFLOW_VERSION = None
CONNECTOR_ID = None

# 轮询配置（可选）
INITIAL_POLL_INTERVAL = 2    # 初始轮询间隔（秒）
MAX_POLL_INTERVAL = 30       # 最大轮询间隔（秒）
MAX_POLL_ATTEMPTS = 120      # 最大轮询次数
```

### 4. 运行脚本

#### 同步执行

在项目目录下打开终端，执行：

```bash
python workflow_sync.py
```

或者在 Windows PowerShell 中：

```powershell
python workflow_sync.py
```

**执行过程**：
1. 脚本会先检查配置是否完整
2. 显示工作流 ID 和输入参数
3. 发送同步执行请求（等待工作流执行完成，最多 10 分钟）
4. 将请求配置和执行结果保存为 JSON 文件

#### 异步执行

在项目目录下打开终端，执行：

```bash
python workflow_async.py
```

或者在 Windows PowerShell 中：

```powershell
python workflow_async.py
```

**执行过程**：
1. 脚本会先检查配置是否完整
2. 显示工作流 ID 和输入参数
3. 发送异步执行请求，获取 `execute_id`
4. 自动开始轮询任务状态（初始间隔 2 秒，指数退避，最大 30 秒）
5. 检测到任务完成（状态为 `Success` 或 `Fail`）后停止轮询
6. 将请求配置和最终执行结果保存为 JSON 文件

**注意事项**：
- 异步执行需要专业版或更高级别的 Coze 账号
- 轮询过程中会实时显示任务状态
- 如果达到最大轮询次数仍未完成，会保存最后一次查询的结果

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

结果已保存到文件: sync_20241018101935.json
```

**特点**：
- 脚本会先执行调用，完成后再保存结果
- 无论请求成功或失败，都会保存原始的请求和响应数据
- 文件名基于任务发起时的北京时间，格式为 `sync_YYYYMMDDHHMMSS.json`

### 异步执行模式

**适用场景**：
- 工作流执行时间较长
- 需要异步处理，不阻塞主程序
- 适合生产环境使用

**执行流程**：
1. 发送异步执行请求（`is_async: true`），获取 `execute_id`
2. 自动开始轮询任务状态（使用查询工作流异步执行结果 API）
3. 检测执行状态（`Success` / `Running` / `Fail`），完成后停止轮询
4. 自动保存请求配置和最终执行结果到 JSON 文件

**轮询策略**：
- 初始间隔：2 秒
- 最大间隔：30 秒（指数退避策略，逐渐增加）
- 自动判断任务状态（`execute_status` 字段），状态为 `Success` 或 `Fail` 时停止轮询
- 最多轮询 120 次（可通过 `MAX_POLL_ATTEMPTS` 配置）

**示例输出**：
```
============================================================
启动 Coze 工作流异步执行
============================================================
工作流 ID: your_workflow_id
输入参数: {
  "param1": "value1",
  "param2": "value2"
}
------------------------------------------------------------
正在发送异步执行请求...

任务 ID (execute_id): 743104097880585****
============================================================

开始轮询任务状态...
------------------------------------------------------------

第 1 次查询... (等待 2 秒)
当前状态: Running
任务正在执行中...

第 2 次查询... (等待 3 秒)
当前状态: Success

任务执行完成！
============================================================

结果已保存到文件: async_20241018101935.json
============================================================
```

---

## 📄 输出文件格式

两个脚本都会自动将结果保存为 JSON 文件，文件命名规则：

**同步执行文件格式**：`sync_YYYYMMDDHHMMSS.json`  
**异步执行文件格式**：`async_YYYYMMDDHHMMSS.json`

**示例**：
- `sync_20241018101935.json`（同步执行）
- `async_20241018101935.json`（异步执行）

**说明**：
- 文件名中的时间戳为任务发起时的北京时间（24小时制）
- 格式：`前缀_年月日时分秒.json`

**JSON 结构**：
```json
{
  "request": {
    "workflow_id": "your_workflow_id",
    "parameters": {
      "param1": "value1",
      "param2": "value2"
    },
    "is_async": false,
    "bot_id": null,
    "app_id": null
  },
  "response": {
    "code": 0,
    "msg": "",
    "data": "...",
    "execute_id": "743104097880585****",
    "debug_url": "https://...",
    "usage": {
      "input_count": 50,
      "output_count": 100,
      "token_count": 150
    }
  }
}
```

**字段说明**：
- `request`：本次运行的所有输入参数和配置（包括所有可选参数）
- `response`：工作流 API 返回的完整响应数据（原始结果，无论成功或失败都会保存）

---

## 🔧 配置说明

### 必需配置

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `YOUR_ACCESS_TOKEN` | Coze API 访问令牌 | 在 Coze 平台生成访问令牌，参考 [准备工作](#) |
| `WORKFLOW_ID` | 工作流唯一标识符 | 在工作流编排页面 URL 中找到，参考 [API 文档](#) |
| `PARAMETERS` | 工作流输入参数 | 根据工作流定义中的输入参数配置，参数名称必须完全一致 |

### 可选配置（两个脚本都支持）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `BOT_ID` | `None` | 需要关联的智能体 ID（部分工作流执行时需要） |
| `APP_ID` | `None` | 工作流关联的扣子应用 ID（仅运行扣子应用中的工作流时需要） |
| `EXT` | `None` | 额外字段，格式：`{"latitude": "39.9042", "longitude": "116.4074", "user_id": "xxx"}` |
| `WORKFLOW_VERSION` | `None` | 工作流版本号（仅资源库工作流有效） |
| `CONNECTOR_ID` | `None` | 渠道 ID，默认 1024（API 渠道） |

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
- **执行工作流**：`POST https://api.coze.cn/v1/workflow/run`
  - 支持同步和异步两种模式（通过 `is_async` 参数控制）
  - 同步模式：等待工作流执行完成后返回结果（超时 10 分钟）
  - 异步模式：立即返回 `execute_id`，需通过查询 API 获取结果
- **查询工作流异步执行结果**：`GET https://api.coze.cn/v1/workflows/{workflow_id}/run_histories/{execute_id}`
  - 仅用于查询异步执行的工作流结果
  - 返回执行状态：`Success` / `Running` / `Fail`

详细的 API 文档请参考项目中的说明文档：
- `coze执行工作流说明.md` - 执行工作流 API 详细文档
- `coze查询工作流异步执行结果说明.md` - 查询异步执行结果 API 详细文档

---

## ⚠️ 注意事项

### 1. 安全性

- **Token 保护**：请妥善保管您的 Access Token，不要提交到版本控制系统
- 建议使用环境变量或配置文件管理敏感信息（生产环境）

### 2. 超时设置

- 同步脚本默认超时为 10 分钟（600 秒）
- 建议执行时间控制在 5 分钟以内，否则不保障执行结果的准确性
- 长时间运行的工作流（超过 10 分钟）必须使用异步模式
- 异步模式超时时间为 24 小时

### 3. 输入参数

- 确保 `PARAMETERS` 中的参数名称与工作流定义中的输入参数名称**完全一致**（包括大小写）
- 注意参数类型匹配（字符串、数字、对象、数组等）
- 如果工作流输入参数为文件类型（如 Image），可以传入文件 URL 或通过「上传文件 API」获取 `file_id` 后传入
- 在工作流编排页面可以查看输入参数列表和类型要求

### 4. 轮询策略（异步模式）

- 异步脚本使用指数退避策略，避免频繁请求
- 初始间隔：2 秒，逐渐增加至最大 30 秒
- 可根据实际情况调整 `INITIAL_POLL_INTERVAL`、`MAX_POLL_INTERVAL` 和 `MAX_POLL_ATTEMPTS`
- 执行状态为 `Success` 或 `Fail` 时自动停止轮询

### 5. 错误处理

- 脚本已包含完善的错误处理机制
- **无论请求成功或失败，都会保存原始结果**，方便排查问题
- 失败时可在保存的 JSON 文件中查看错误信息和错误码
- 建议在生产环境中增加日志记录功能
- 如果遇到问题，可以根据返回的 `logid` 联系扣子团队获取帮助

### 6. 文件保存时机

- **同步模式**：先执行调用，完成后再保存结果
- **异步模式**：先执行调用获取 `execute_id`，轮询完成后保存最终结果
- 如果启动失败或未获取到 `execute_id`，会立即保存启动响应

---

## ❓ 常见问题

### Q1: 如何获取 Access Token？

A: 通过 Coze 平台的 OAuth 机制获取。具体方法请参考 [Coze 官方文档](https://www.coze.cn/open/docs)。

### Q2: 如何获取 Workflow ID？

A: 在 Coze 平台创建工作流后，可以在工作流详情页面找到 ID。

### Q3: 同步执行超时怎么办？

A: 可以修改脚本中的 `timeout` 参数，或者改用异步执行模式。

### Q4: 异步任务一直处于 Running 状态？

A: 
- 检查工作流配置是否正确
- 增加 `MAX_POLL_ATTEMPTS` 的值，给任务更多完成时间
- 查看保存的 JSON 文件中的 `debug_url`，通过可视化界面查看工作流执行详情
- 输出节点的输出数据最多保存 24 小时，结束节点为 7 天

### Q5: 输入参数不匹配？

A: 
- 确保参数名称与工作流定义中的输入参数名称完全一致，注意大小写
- 在工作流编排页面查看输入参数列表和类型要求
- 检查参数类型是否正确（字符串、数字、对象、数组等）
- 如果工作流需要关联智能体（如包含数据库节点、变量节点），需要设置 `BOT_ID`

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

### v1.1 (2025-01-XX)

- 🔄 修正 API 参数名称：`INPUTS` → `PARAMETERS`，符合官方 API 规范
- 🔄 修正异步执行参数：`async` → `is_async`
- 🔄 修正返回字段：`run_id` → `execute_id`
- 🔄 修正查询 API 端点：使用正确的 URL 格式 `/workflows/{workflow_id}/run_histories/{execute_id}`
- 🔄 修正状态字段：使用 `execute_status`（值为 `Success`/`Running`/`Fail`）
- 📝 更新文件命名规则：使用北京时间格式 `sync_YYYYMMDDHHMMSS.json` 和 `async_YYYYMMDDHHMMSS.json`
- 📝 统一保存逻辑：无论成功失败都保存原始请求和响应数据
- ✅ 添加可选参数支持：`BOT_ID`、`APP_ID`、`EXT`、`WORKFLOW_VERSION`、`CONNECTOR_ID`
- 📚 完善文档说明，补充脚本执行方法和配置说明

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

