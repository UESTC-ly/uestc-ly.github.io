from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "examples" / "minimal-rag" / "minimal_rag.py"


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_cli_text_output_is_successful_and_deterministic() -> None:
    arguments = ("--query", "RAG 如何回答问题？", "--top-k", "2")

    first = run_cli(*arguments)
    second = run_cli(*arguments)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout
    for label in (
        "语料数量：",
        "Chunk 数量：",
        "查询 Embedding：",
        "检索结果：",
        "上下文：",
        "Prompt：",
        "回答：",
        "引用位置：",
    ):
        assert label in first.stdout
    assert first.stderr == ""


def test_cli_json_no_answer_path() -> None:
    completed = run_cli("--query", "!!!", "--json")

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["query_embedding"] == {}
    assert payload["retrieved"] == []
    assert payload["citations"] == []
    assert payload["answer"] == "未找到足够相关的资料，无法基于当前语料回答。"


def test_cli_rejects_empty_query() -> None:
    completed = run_cli("--query", "   ")

    assert completed.returncode == 2
    assert "query 不能为空" in completed.stderr
