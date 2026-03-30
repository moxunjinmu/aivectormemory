"""自动摘要生成器"""
import os

from aivectormemory.config import SUMMARY_THRESHOLD


def generate_summary(content: str) -> str | None:
    """生成摘要。内容超过 SUMMARY_THRESHOLD 字符时生成。

    规则：取前 200 字 + "..."
    预留：AIVM_SUMMARIZER 环境变量可指定外部摘要服务 URL
    """
    if len(content) <= SUMMARY_THRESHOLD:
        return None

    summarizer_url = os.getenv('AIVM_SUMMARIZER', '')
    if summarizer_url:
        try:
            import json
            import urllib.request
            req = urllib.request.Request(
                summarizer_url,
                data=json.dumps({'content': content}).encode(),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read())['summary']
        except Exception:
            pass  # 回退到规则摘要

    return content[:200] + '...'
