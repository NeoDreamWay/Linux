#!/usr/bin/env python3
"""
MCP 作业服务器
功能：提供打招呼和数学计算工具
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("student-mcp-server")


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="greet",
            description="向用户发送问候语",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "用户姓名"
                    }
                },
                "required": ["username"]
            }
        ),
        Tool(
            name="math_compute",
            description="执行基础数学运算",
            inputSchema={
                "type": "object",
                "properties": {
                    "formula": {
                        "type": "string",
                        "description": "数学表达式，例如 2+3*4"
                    }
                },
                "required": ["formula"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "greet":
        user = arguments.get("username", "同学")
        msg = f"你好，{user}！欢迎来到 MCP 作业演示！"
        return [TextContent(type="text", text=msg)]

    elif name == "math_compute":
        expr = arguments.get("formula", "")
        try:
            # 安全计算：只允许数字和基本运算符
            allowed = set("0123456789+-*/.() ")
            if not all(c in allowed for c in expr):
                raise ValueError("表达式包含非法字符")
            result = eval(expr)
            return [TextContent(type="text", text=f"计算结果：{expr} = {result}")]
        except Exception as e:
            return [TextContent(type="text", text=f"计算出错：{str(e)}")]

    else:
        return [TextContent(type="text", text=f"未知工具：{name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
