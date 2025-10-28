# Coze 工作流 API 调用说明文档

本文档基于 Coze 官方 API 文档整理，详细说明了工作流执行调用和异步任务查询的接口规范、请求参数、响应参数等内容，供开发者参考使用。

---

## 一、工作流执行调用 API

### 1. 接口概述

该接口用于触发 Coze 平台上的指定工作流执行，支持同步和异步两种执行模式。

### 2. 请求方式

- **HTTP 方法**：`POST`
- **请求 URL**：`https://api.coze.cn/v1/workflow/run`

### 3. 请求头（Headers）

| 参数名           | 类型   | 必填 | 说明                                  |
| ---------------- | ------ | ---- | ------------------------------------- |
| `Authorization`  | string | 是   | Bearer Token，格式：`Bearer {YOUR_ACCESS_TOKEN}` |
| `Content-Type`   | string | 是   | 固定值：`application/json`             |

### 4. 请求参数（Request Body）

请求体应为 JSON 格式，包含以下字段：

| 参数名          | 类型    | 必填 | 说明                                                                 |
| --------------- | ------- | ---- | -------------------------------------------------------------------- |
| `workflow_id`   | string  | 是   | 要执行的工作流的唯一标识符                                           |
| `inputs`        | object  | 否   | 工作流所需的输入参数，键值对形式                                     |
| `async`         | boolean | 否   | 是否以异步方式执行，默认为 `false`（同步执行）                       |
| `callback_url`  | string  | 否   | 异步执行时的回调 URL，工作流完成后将向该地址发送通知                 |

#### 请求参数说明

- **workflow_id**：必填参数，用于指定要执行的工作流。需要在 Coze 平台创建并获取工作流 ID。
- **inputs**：可选参数，如果工作流需要输入参数，可以通过该字段传递。参数名称必须与工作流定义中的输入参数名称一致。
- **async**：可选参数，控制执行模式。设置为 `true` 时，接口立即返回任务 ID，工作流在后台异步执行；设置为 `false` 时，接口等待工作流执行完成后再返回结果。
- **callback_url**：可选参数，仅当 `async` 为 `true` 时有效。工作流执行完成后，系统将向该 URL 发送 POST 请求，通知执行结果。

#### 示例请求体

**同步执行示例**：
```json
{
  "workflow_id": "your_workflow_id",
  "inputs": {
    "param1": "value1",
    "param2": "value2"
  },
  "async": false
}
```

**异步执行示例**：
```json
{
  "workflow_id": "your_workflow_id",
  "inputs": {
    "param1": "value1",
    "param2": "value2"
  },
  "async": true,
  "callback_url": "https://your.callback.url"
}
```

### 5. 响应参数（Response）

根据 `async` 参数的值，返回结果有所不同：

#### 5.1 同步执行响应（`async` 为 `false`）

| 参数名   | 类型   | 说明                                                                 |
| -------- | ------ | -------------------------------------------------------------------- |
| `run_id` | string | 工作流运行的唯一标识符                                               |
| `status` | string | 执行状态，通常为 `completed`（成功）或 `failed`（失败）             |
| `output` | object | 工作流的输出结果，键值对形式，仅在状态为 `completed` 时存在         |
| `error`  | object | 错误信息，仅在状态为 `failed` 时存在，包含 `code` 和 `message` 字段 |
| `created_at` | string | 运行开始时间，ISO 8601 格式（如：`2025-10-28T15:58:40Z`）         |
| `updated_at` | string | 运行结束时间，ISO 8601 格式                                         |

**同步执行成功示例响应**：
```json
{
  "run_id": "run123",
  "status": "completed",
  "output": {
    "result": "success",
    "data": {
      "key1": "value1",
      "key2": "value2"
    }
  },
  "created_at": "2025-10-28T15:58:40Z",
  "updated_at": "2025-10-28T15:59:00Z"
}
```

**同步执行失败示例响应**：
```json
{
  "run_id": "run123",
  "status": "failed",
  "error": {
    "code": "WORKFLOW_EXECUTION_ERROR",
    "message": "Workflow execution failed due to invalid input parameters."
  },
  "created_at": "2025-10-28T15:58:40Z",
  "updated_at": "2025-10-28T15:58:45Z"
}
```

#### 5.2 异步执行响应（`async` 为 `true`）

| 参数名      | 类型   | 说明                                     |
| ----------- | ------ | ---------------------------------------- |
| `run_id`    | string | 工作流运行的唯一标识符，用于后续查询状态 |
| `status`    | string | 任务状态，初始为 `pending`               |
| `created_at` | string | 运行开始时间，ISO 8601 格式              |

**异步执行示例响应**：
```json
{
  "run_id": "run123",
  "status": "pending",
  "created_at": "2025-10-28T15:58:40Z"
}
```

对于异步执行的任务，需要通过工作流历史查询 API 或回调 URL 来获取执行结果。

### 6. 错误响应

当请求发生错误时，API 会返回相应的 HTTP 状态码和错误信息：

**错误响应格式**：
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message description"
  }
}
```

常见错误码：
- `400 Bad Request`：请求参数错误
- `401 Unauthorized`：认证失败，Access Token 无效或过期
- `404 Not Found`：工作流不存在
- `500 Internal Server Error`：服务器内部错误

---

## 二、异步执行任务查询 API（工作流历史查询）

### 1. 接口概述

该接口用于查询特定工作流执行的历史记录和状态，主要用于查询异步执行的任务结果。

### 2. 请求方式

- **HTTP 方法**：`GET`
- **请求 URL**：`https://api.coze.cn/v1/workflow/history/{run_id}`

其中，`{run_id}` 为路径参数，表示要查询的工作流运行的唯一标识符。

### 3. 请求头（Headers）

| 参数名          | 类型   | 必填 | 说明                                  |
| --------------- | ------ | ---- | ------------------------------------- |
| `Authorization` | string | 是   | Bearer Token，格式：`Bearer {YOUR_ACCESS_TOKEN}` |

### 4. 路径参数（Path Parameters）

| 参数名   | 类型   | 必填 | 说明                         |
| -------- | ------ | ---- | ---------------------------- |
| `run_id` | string | 是   | 工作流运行的唯一标识符       |

### 5. 查询参数（Query Parameters）

可选查询参数，用于筛选和分页：

| 参数名        | 类型   | 必填 | 说明                                                                 |
| ------------- | ------ | ---- | -------------------------------------------------------------------- |
| `workflow_id` | string | 否   | 工作流的唯一标识符，若指定则查询该工作流的历史记录                   |
| `status`      | string | 否   | 过滤指定状态的运行记录，如 `completed`、`failed`、`pending`、`running` 等 |
| `limit`       | int    | 否   | 每页返回的记录数，默认为 10                                          |
| `offset`      | int    | 否   | 分页偏移量，默认为 0                                                 |

**示例请求 URL**：
```
GET https://api.coze.cn/v1/workflow/history/run123
```

或带查询参数：
```
GET https://api.coze.cn/v1/workflow/history/run123?status=completed&limit=5&offset=0
```

### 6. 响应参数（Response）

成功调用后，服务器将返回 JSON 格式的响应，包含以下字段：

| 参数名        | 类型    | 说明                                                                 |
| ------------- | ------- | -------------------------------------------------------------------- |
| `run_id`      | string  | 工作流运行的唯一标识符                                               |
| `workflow_id` | string  | 关联的工作流标识符                                                   |
| `status`      | string  | 执行状态，可能的值包括：`pending`、`running`、`completed`、`failed` 等 |
| `inputs`      | object  | 执行时提供的输入参数                                                 |
| `outputs`     | object  | 工作流的输出结果，键值对形式，仅在状态为 `completed` 时存在         |
| `error`       | object  | 错误信息，仅在状态为 `failed` 时存在，包含 `code` 和 `message` 字段 |
| `created_at` | string | 工作流运行的创建时间（执行开始时间），ISO 8601 格式                 |
| `updated_at`  | string  | 工作流运行的最后更新时间（执行结束时间），ISO 8601 格式             |

#### 状态值说明

- **pending**：任务已创建，等待执行
- **running**：任务正在执行中
- **completed**：任务执行成功完成
- **failed**：任务执行失败

#### 响应示例

**任务成功完成示例**：
```json
{
  "run_id": "run123",
  "workflow_id": "your_workflow_id",
  "status": "completed",
  "inputs": {
    "param1": "value1",
    "param2": "value2"
  },
  "outputs": {
    "result": "success",
    "data": {
      "key1": "value1",
      "key2": "value2"
    }
  },
  "created_at": "2025-10-28T15:58:40Z",
  "updated_at": "2025-10-28T16:00:00Z"
}
```

**任务执行中示例**：
```json
{
  "run_id": "run123",
  "workflow_id": "your_workflow_id",
  "status": "running",
  "inputs": {
    "param1": "value1",
    "param2": "value2"
  },
  "created_at": "2025-10-28T15:58:40Z",
  "updated_at": "2025-10-28T15:59:30Z"
}
```

**任务失败示例**：
```json
{
  "run_id": "run123",
  "workflow_id": "your_workflow_id",
  "status": "failed",
  "inputs": {
    "param1": "value1",
    "param2": "value2"
  },
  "error": {
    "code": "WORKFLOW_EXECUTION_ERROR",
    "message": "Workflow execution failed due to timeout."
  },
  "created_at": "2025-10-28T15:58:40Z",
  "updated_at": "2025-10-28T15:59:45Z"
}
```

**任务等待执行示例**：
```json
{
  "run_id": "run123",
  "workflow_id": "your_workflow_id",
  "status": "pending",
  "inputs": {
    "param1": "value1",
    "param2": "value2"
  },
  "created_at": "2025-10-28T15:58:40Z",
  "updated_at": "2025-10-28T15:58:40Z"
}
```

### 7. 错误响应

当请求发生错误时，API 会返回相应的 HTTP 状态码和错误信息：

**错误响应格式**：
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message description"
  }
}
```

常见错误码：
- `400 Bad Request`：请求参数错误
- `401 Unauthorized`：认证失败，Access Token 无效或过期
- `404 Not Found`：指定的 `run_id` 不存在
- `500 Internal Server Error`：服务器内部错误

---

## 三、使用流程说明

### 1. 同步执行流程

1. 调用工作流执行 API，设置 `async` 为 `false` 或不传递该参数
2. 等待 API 返回执行结果
3. 检查返回的 `status` 字段，判断执行是否成功
4. 如果成功，从 `output` 字段获取结果；如果失败，从 `error` 字段获取错误信息

### 2. 异步执行流程

1. 调用工作流执行 API，设置 `async` 为 `true`
2. 获取返回的 `run_id`
3. 定期调用工作流历史查询 API，使用 `run_id` 查询任务状态
4. 当 `status` 变为 `completed` 或 `failed` 时，获取最终结果或错误信息

**或者**：
1. 调用工作流执行 API，设置 `async` 为 `true`，并设置 `callback_url`
2. 获取返回的 `run_id`
3. 等待回调通知，或定期查询任务状态作为备用方案

### 3. 轮询建议

对于异步任务，建议采用指数退避策略进行轮询：
- 初始轮询间隔：1-2 秒
- 最大轮询间隔：30 秒
- 最大轮询次数：根据业务需求设定超时时间

---

## 四、注意事项

### 1. 认证（Authentication）

所有 API 请求都需要在请求头中包含有效的 `Authorization` 字段，格式为：
```
Authorization: Bearer {YOUR_ACCESS_TOKEN}
```

Access Token 可通过 Coze 平台的 OAuth 机制获取。请妥善保管 Access Token，避免泄露。

### 2. 异步执行结果查询

对于异步执行的工作流：
- 可以通过工作流历史查询 API 定期查询执行状态
- 如果设置了 `callback_url`，系统会在任务完成时主动推送结果
- 建议同时使用轮询和回调两种方式，确保可靠获取结果

### 3. 错误处理

- 始终检查响应中的 `status` 字段，判断请求是否成功
- 对于失败的情况，检查 `error` 字段中的 `code` 和 `message`，进行相应的错误处理
- 建议实现重试机制，对于网络错误或临时性错误进行重试

### 4. 超时处理

- 同步执行的工作流可能存在执行时间较长的情况，需要设置合理的超时时间
- 对于长时间运行的工作流，建议使用异步执行模式

### 5. 输入参数验证

- 调用前请确保 `inputs` 中的参数名称与工作流定义中的输入参数名称一致
- 注意参数类型匹配，如字符串、数字、对象等

### 6. 时间格式

所有时间字段均使用 ISO 8601 格式，示例：`2025-10-28T15:58:40Z`

---

## 五、参考资料

- [工作流执行调用文档](https://www.coze.cn/open/docs/developer_guides/workflow_run)
- [工作流历史查询文档](https://www.coze.cn/open/docs/developer_guides/workflow_history)
- [Coze 开放平台文档](https://www.coze.cn/open/docs)

---

**文档版本**：v1.0  
**最后更新**：2025-01-28  
**基于 Coze 官方 API 文档整理**

