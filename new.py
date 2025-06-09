import os
import asyncio
import json
import logging
from typing import List, Dict, Any

import aiohttp
from git import Repo

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 설정 읽기
NOTION_MCP_URL = os.getenv("NOTION_MCP_URL", "https://mcp.notion.example.com/jsonrpc")
PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "YOUR_PARENT_PAGE_ID")
GIT_REPO_PATH = os.getenv("GIT_REPO_PATH", ".")
MAX_COMMITS = int(os.getenv("MAX_COMMITS", "20"))

class NotionMCPClient:
    def __init__(self, endpoint: str, parent_page_id: str, token: str):
        self.endpoint = endpoint
        self.parent = {"page_id": parent_page_id}
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

    def _make_rpc_call(self, method: str, params: Dict[str, Any], call_id: int) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": call_id,
            "method": method,
            "params": params
        }

    async
