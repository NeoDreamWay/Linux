#!/usr/bin/env python3
"""
系统信息查询服务
基于 JSON-RPC 2.0 协议，提供系统信息和时间查询接口
"""

import json
import sys
import platform
import time
from typing import Any, Dict, List


class SystemQueryService:
    """系统查询服务类"""

    JSONRPC_VERSION = "2.0"

    TOOL_DEFINITIONS: List[Dict[str, str]] = [
        {"name": "system_info", "description": "获取操作系统类型及内核版本"},
        {"name": "current_time", "description": "获取当前系统时间"}
    ]

    def __init__(self):
        self.server_name = "linux-info-server"
        self.server_version = "1.0.0"

    def _build_response(self, request_id: Any, result: Dict = None, 
                        error: Dict = None) -> Dict:
        """构造标准 JSON-RPC 响应"""
        payload = {
            "jsonrpc": self.JSONRPC_VERSION,
            "id": request_id
        }
        if error:
            payload["error"] = error
        else:
            payload["result"] = result
        return payload

    def _handle_initialize(self, req_id: Any) -> Dict:
        """处理初始化请求"""
        return self._build_response(
            req_id,
            result={
                "serverInfo": {
                    "name": self.server_name,
                    "version": self.server_version
                }
            }
        )

    def _handle_tools_list(self, req_id: Any) -> Dict:
        """处理工具列表请求"""
        return self._build_response(
            req_id,
            result={"tools": self.TOOL_DEFINITIONS}
        )

    def _handle_tools_call(self, req_id: Any, params: Dict) -> Dict:
        """处理工具调用请求"""
        tool_name = params.get("name", "")

        if tool_name == "system_info":
            content = f"操作系统: {platform.system()}, 内核版本: {platform.release()}"
        elif tool_name == "current_time":
            content = time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return self._build_response(
                req_id,
                error={"code": -1, "message": f"未找到工具: {tool_name}"}
            )

        return self._build_response(
            req_id,
            result={
                "content": [
                    {"type": "text", "text": content}
                ]
            }
        )

    def dispatch(self, request: Dict) -> Dict:
        """请求分发器"""
        req_id = request.get("id")
        method = request.get("method")

        if method == "initialize":
            return self._handle_initialize(req_id)
        elif method == "tools/list":
            return self._handle_tools_list(req_id)
        elif method == "tools/call":
            return self._handle_tools_call(req_id, request.get("params", {}))
        else:
            return self._build_response(
                req_id,
                error={"code": -32601, "message": f"不支持的方法: {method}"}
            )

    def run(self):
        """主循环：从标准输入读取 JSON-RPC 请求并响应"""
        for raw_line in sys.stdin:
            stripped = raw_line.strip()
            if not stripped:
                continue
            try:
                request = json.loads(stripped)
            except json.JSONDecodeError:
                continue

            response = self.dispatch(request)
            print(json.dumps(response, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    service = SystemQueryService()
    service.run()
