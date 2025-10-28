
# 查询工作流异步执行结果

> 工作流异步运行后，查看执行结果。  
> 调用「执行工作流 API」时，如果选择异步执行工作流，响应信息中会返回 `execute_id`，开发者可以通过本接口查询指定事件的执行结果。

## 限制说明

- 本 API 的流控限制请参见 [API 介绍](#)。
- 工作流的**输出节点**的输出数据最多保存 **24 小时**，**结束节点**为 **7 天**。
- 输出节点的输出内容**超过 1 MB** 时，**无法保证返回内容的完整性**。

---

## 基础信息

| 项目 | 内容 |
|------|------|
| 请求方式 | `GET` |
| 请求地址 | `https://api.coze.cn/v1/workflows/:workflow_id/run_histories/:execute_id` |
| 权限 | `listRunHistory`（确保访问令牌已开通该权限，详见 [鉴权方式](#)） |

---

## 请求参数

### Header

| 参数 | 取值 | 说明 |
|------|------|------|
| Authorization | `Bearer $Access_Token` | 访问令牌，用于身份验证。参考 [准备工作](#) 生成。 |
| Content-Type | `application/json` | 请求正文格式。 |

### Path

| 参数 | 类型 | 是否必选 | 示例 | 说明 |
|------|------|----------|------|------|
| workflow_id | String | 可选 | `73505836754923***` | 已发布的 Workflow ID。URL 中 `workflow_id` 参数后的数字即为 ID。 |
| execute_id | String | 可选 | `743104097880585****` | 异步执行事件 ID，由「执行工作流 API」异步模式返回。 |

---

## 返回参数

| 参数 | 类型 | 示例 | 说明 |
|------|------|------|------|
| code | Long | `0` | 调用状态码。`0` 表示成功，其他值表示失败，详见 `msg`。 |
| msg | String | `""` | 错误信息，成功时为空。 |
| data | Array of [WorkflowExecuteHistory](#workflowexecutehistory) |  | 异步执行结果数组，**仅含一个对象**。 |
| detail | [ResponseDetail](#responsedetail) | `{"logid":"20241210152726467C48D89D6DB2****"}` | 请求详情，含日志 ID，用于排查问题。 |

---

### WorkflowExecuteHistory

| 参数 | 类型 | 示例 | 说明 |
|------|------|------|------|
| execute_id | Long | `743104097880585****` | 工作流执行 ID。 |
| execute_status | String | `Success` | 执行状态：`Success` / `Running` / `Fail`。 |
| bot_id | Long | `75049216555930****` | 关联的智能体 ID，未指定时返回 `0`。 |
| connector_id | Long | `1024` | 发布渠道 ID，默认 `1024`（API）。 |
| connector_uid | String | `123` | 用户 ID，未指定时返回 Token 申请人的扣子 ID。 |
| run_mode | Integer | `0` | 运行方式：`0` 同步，`1` 流式，`2` 异步。 |
| output | String | `{"Output":"{\"content_type\":1,\"data\":\"来找姐姐有什么事呀\",...}"}` | 工作流输出（JSON 序列化字符串）。包含：<br>- 结束节点：`"Output"` 键<br>- 输出节点：节点名作为键 |
| create_time | Long | `1730174063` | 开始时间（Unix 秒）。 |
| update_time | Long | `1730174063` | 最近更新时间（Unix 秒）。 |
| node_execute_status | JSON Map |  | 各输出节点运行状态，结构见 [NodeExecuteStatus](#nodeexecutestatus)。<br>内容 >1 MB 时建议用「查询工作流节点输出 API」逐节点获取。 |
| error_code | String | `""` | 失败时的错误码，`0` 表示成功。 |
| error_msg | String | `""` | 失败时的错误描述。 |
| debug_url | String | `https://www.coze.cn/work_flow?execute_id=...` | 可视化调试页面，**7 天内有效**。 |
| usage | [Usage](#usage) | `{"input_count":50,"token_count":150,"output_count":100}` | Token 消耗（仅供参考，以账单为准）。 |
| is_output_trimmed | Boolean | `false` | `true` 表示输出因过大被截断。 |
| log_id | String | `20241029152003BC531DC784F1897B***` | 异步运行日志 ID，用于异常排查。 |

---

### NodeExecuteStatus

| 参数 | 类型 | 示例 | 说明 |
|------|------|------|------|
| node_id | String | `node_123` | 节点 ID。 |
| is_finish | Boolean | `true` | 节点是否已结束。 |
| loop_index | Long | `2` | 当前在循环节点中的次数（从 0 开始）。<br>仅对**未嵌套子工作流**的循环节点返回。 |
| batch_index | Long | `3` | 当前在批处理节点中的次数（从 0 开始）。<br>仅对**未嵌套子工作流**的批处理节点返回。 |
| update_time | Long | `1730174063` | 节点最近运行时间（Unix 秒）。 |
| sub_execute_id | String | `743104097880585****` | 子工作流执行 ID（若存在）。 |
| node_execute_uuid | String | `78923456777*****` | 节点单次执行唯一标识，用于追踪。 |

---

### Usage

| 参数 | 类型 | 示例 | 说明 |
|------|------|------|------|
| input_count | Integer | `50` | 输入 Token 数。 |
| output_count | Integer | `100` | 输出 Token 数。 |
| token_count | Integer | `150` | 总 Token 数。 |

---

### ResponseDetail

| 参数 | 类型 | 示例 | 说明 |
|------|------|------|------|
| logid | String | `20241210152726467C48D89D6DB2****` | 请求日志 ID，异常时随错误码一并提交给扣子团队。 |

---

## 示例

### 请求示例

```bash
curl --location --request GET \
'https://api.coze.cn/v1/workflows/742963539464539****/run_histories/743104097880585****' \
--header 'Authorization: Bearer pat_xitq9LWlowpX3qGCih1lwpAdzvXNqgmpfhpV28HLWFypY37xR5Uaj2GioN****' \
--header 'Content-Type: application/json'
```

### 返回示例

```json
{
  "detail": { "logid": "20241029152003BC531DC784F1897B****" },
  "code": 0,
  "msg": "",
  "data": [
    {
      "update_time": 1730174065,
      "usage": { "input_count": 50, "token_count": 150, "output_count": 100 },
      "output": "{\"Output\":\"{\\\"content_type\\\":1,\\\"data\\\":\\\"来找姐姐有什么事呀\\\",\\\"original_result\\\":null,\\\"type_for_model\\\":2}\"}",
      "bot_id": "742963486232569****",
      "execute_status": "Success",
      "connector_uid": "223687073464****",
      "run_mode": 2,
      "connector_id": "1024",
      "logid": "20241029115423ED85C3401395715F726E",
      "debug_url": "https://www.coze.cn/work_flow?execute_id=743104097880585****&space_id=730976060439760****&workflow_id=742963539464539****",
      "error_code": "",
      "error_msg": "",
      "execute_id": "743104097880585****",
      "create_time": 1730174063
    }
  ]
}
```

---

## 错误码

> 若 `code ≠ 0`，表示调用失败，可通过 `msg` 查看详细错误信息，并参考「[错误码文档](#)」获取解决方案。
