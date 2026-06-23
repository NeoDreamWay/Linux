#!/usr/bin/env python3
"""
MCP 工具服务
提供问候语和随机数生成功能
"""

import json
import sys
import random
from functools import partial

# ── 常量定义 ──────────────────────────────
JSONRPC_VER = "2.0"

AVAILABLE_TOOLS = (
    {"name": "hello",             "description": "返回一条欢迎消息"},
    {"name": "get_random_number", "description": "生成 1~100 范围内的随机整数"},
)

SERVER_META = {"name": "mcp-student-server", "version": "1.0"}

# ── 工具函数 ──────────────────────────────
def make_text_response(text: str) -> dict:
    return {"content": [{"type": "text", "text": text}]}


def make_error(code: int, message: str) -> dict:
    return {"code": code, "message": message}


def make_jsonrpc(id_, result=None, error=None) -> dict:
    payload = {"jsonrpc": JSONRPC_VER, "id": id_}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    return payload


# ── 业务逻辑 ──────────────────────────────
def handle_hello() -> str:
    return "Hello, MCP!"


def handle_random() -> str:
    return str(random.randint(1, 100))


TOOL_REGISTRY = {
    "hello": handle_hello,
    "get_random_number": handle_random,
}


# ── 请求处理器 ──────────────────────────────
def process_initialize(request_id):
    return make_jsonrpc(request_id, result={"serverInfo": SERVER_META})


def process_tools_list(request_id):
    return make_jsonrpc(request_id, result={"tools": list(AVAILABLE_TOOLS)})


def process_tools_call(request_id, params: dict):
    tool_name = params.get("name")
    handler = TOOL_REGISTRY.get(tool_name)

    if handler is None:
        return make_jsonrpc(
            request_id,
            error=make_error(-1, f"未知工具: {tool_name}")
        )

    result_text = handler()
    return make_jsonrpc(request_id, result=make_text_response(result_text))


METHOD_MAP = {
    "initialize": process_initialize,
    "tools/list": process_tools_list,
    "tools/call": process_tools_call,
}


# ── 主入口 ──────────────────────────────
def main():
    stdin = sys.stdin
    stdout = sys.stdout

    for line in stdin:
        if not line:
            break

        try:
            req = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue

        req_id = req.get("id")
        method = req.get("method")

        processor = METHOD_MAP.get(method)
        if processor is None:
            resp = make_jsonrpc(
                req_id,
                error=make_error(-32601, f"Method not found: {method}")
            )
        else:
            if method == "tools/call":
                resp = processor(req_id, req.get("params", {}))
            else:
                resp = processor(req_id)

        stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
        stdout.flush()


if __name__ == "__main__":
    main()
