---
name: get_weather
description: 查询指定城市的实时天气信息
---

## 步骤

1. 使用 `fetch_url` 工具访问 `https://wttr.in/{城市名}?format=3`
2. 解析返回的天气数据
3. 以友好的格式回复用户

## 示例

查询北京天气: `fetch_url("https://wttr.in/Beijing?format=3")`
