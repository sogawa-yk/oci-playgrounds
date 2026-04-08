#!/usr/bin/env python3
"""OCI Enterprise AI - file_search + サーバー側ステート管理バグ検証スクリプト

file_search ツールと previous_response_id / Conversations API を組み合わせた際の
json_parse_error が製品バグか使い方の問題かを切り分けるためのテストスクリプト。

Usage:
    python verify_file_search_bug.py              # 全テスト×3回
    python verify_file_search_bug.py --quick      # 全テスト×1回
    python verify_file_search_bug.py --test T04   # 特定テストのみ
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime

import httpx
from dotenv import load_dotenv
from oci_genai_auth import (
    OciInstancePrincipalAuth,
    OciResourcePrincipalAuth,
    OciSessionAuth,
    OciUserPrincipalAuth,
)
from openai import OpenAI

load_dotenv()

# ---------- 設定 ----------
VECTOR_STORE_ID = os.environ.get(
    "VECTOR_STORE_ID",
    "vs_kix_tb41acvu0g88kunindnu77axz95w6yu35axn50tt7y2rmfnd",
)
MODEL = os.environ.get("GENAI_MODEL_ID", "openai.gpt-oss-120b")
ALT_MODEL = os.environ.get("GENAI_ALT_MODEL_ID", "")
REGION = os.environ.get("OCI_REGION", "ap-osaka-1")
BASE_URL = f"https://inference.generativeai.{REGION}.oci.oraclecloud.com/openai/v1"
TOOLS = [{"type": "file_search", "vector_store_ids": [VECTOR_STORE_ID]}]
DELAY_BETWEEN_TESTS = 2  # seconds

# テスト用質問ペア
Q1_SEARCH = "OCI API Gatewayとは？"
Q2_SEARCH = "その主な機能を3つ挙げて"
Q1_TEXT = "2+2は？"
Q2_TEXT = "それを3倍して"


# ---------- テスト結果 ----------
@dataclass
class TestResult:
    test_id: str
    description: str
    status: str = ""  # PASS, FAIL, ERROR, SKIP
    error_message: str = ""
    error_type: str = ""
    response_id: str = ""
    elapsed_ms: float = 0.0
    run_number: int = 0
    request_log: list[dict] = field(default_factory=list)
    response_log: list[dict] = field(default_factory=list)


# ---------- HTTP ロギング ----------
class LoggingTransport(httpx.BaseTransport):
    """リクエスト/レスポンスの JSON body をキャプチャするトランスポート。"""

    def __init__(self, transport: httpx.BaseTransport):
        self._transport = transport
        self.request_logs: list[dict] = []
        self.response_logs: list[dict] = []

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        req_body = None
        if request.content:
            try:
                req_body = json.loads(request.content)
            except (json.JSONDecodeError, UnicodeDecodeError):
                req_body = "<binary>"
        self.request_logs.append({
            "method": str(request.method),
            "url": str(request.url),
            "body": req_body,
        })

        response = self._transport.handle_request(request)

        resp_body = None
        try:
            raw = response.read()
            resp_body = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError):
            resp_body = "<non-json>"
        except Exception:
            resp_body = "<read-error>"
        self.response_logs.append({
            "status_code": response.status_code,
            "body": resp_body,
        })
        return response


# ---------- OCI 認証 & クライアント ----------
def _build_auth():
    profile = os.environ.get("OCI_PROFILE", "DEFAULT")
    if os.environ.get("OCI_RESOURCE_PRINCIPAL_VERSION"):
        return OciResourcePrincipalAuth()
    for builder in [
        lambda: OciSessionAuth(profile_name=profile),
        lambda: OciUserPrincipalAuth(profile_name=profile),
        OciInstancePrincipalAuth,
    ]:
        try:
            return builder()
        except Exception:
            pass
    raise RuntimeError("OCI auth failed")


def _build_client() -> tuple[OpenAI, LoggingTransport]:
    """OpenAI クライアントとロギングトランスポートを返す。"""
    base_transport = httpx.HTTPTransport()
    logging_transport = LoggingTransport(base_transport)
    http_client = httpx.Client(
        auth=_build_auth(),
        transport=logging_transport,
    )
    client = OpenAI(
        base_url=BASE_URL,
        api_key="not-used",
        project=os.environ["OCI_GENAI_PROJECT"],
        http_client=http_client,
    )
    return client, logging_transport


# ---------- テスト実行ラッパー ----------
def run_test(test_id: str, description: str, fn, runs: int = 3) -> list[TestResult]:
    results = []
    for i in range(runs):
        result = TestResult(test_id=test_id, description=description, run_number=i + 1)
        start = time.monotonic()
        try:
            fn(result)
            if not result.status:
                result.status = "PASS"
        except Exception as exc:
            result.status = "FAIL" if "error" in str(exc).lower() or "400" in str(exc) else "ERROR"
            result.error_message = str(exc)
            result.error_type = type(exc).__name__
        result.elapsed_ms = round((time.monotonic() - start) * 1000, 1)
        results.append(result)
        if i < runs - 1:
            time.sleep(DELAY_BETWEEN_TESTS)
    return results


# ---------- テスト関数 ----------

def t01(result: TestResult):
    """ベースライン: ステートなし、ツールなし"""
    client, log = _build_client()
    r = client.responses.create(model=MODEL, input=Q1_TEXT)
    result.response_id = r.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t02(result: TestResult):
    """ベースライン: ステートなし、file_search あり"""
    client, log = _build_client()
    r = client.responses.create(model=MODEL, input=Q1_SEARCH, tools=TOOLS)
    result.response_id = r.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t03(result: TestResult):
    """previous_response_id、ツールなし、2ターン"""
    client, log = _build_client()
    r1 = client.responses.create(model=MODEL, input=Q1_TEXT, store=True)
    r2 = client.responses.create(
        model=MODEL, input=Q2_TEXT, previous_response_id=r1.id,
    )
    result.response_id = r2.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t04(result: TestResult):
    """【既知バグ】previous_response_id + file_search、2ターン"""
    client, log = _build_client()
    r1 = client.responses.create(
        model=MODEL, input=Q1_SEARCH, tools=TOOLS, store=True,
    )
    r2 = client.responses.create(
        model=MODEL, input=Q2_SEARCH, previous_response_id=r1.id, tools=TOOLS,
    )
    result.response_id = r2.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t05(result: TestResult):
    """previous_response_id、file_search はターン1のみ"""
    client, log = _build_client()
    r1 = client.responses.create(
        model=MODEL, input=Q1_SEARCH, tools=TOOLS, store=True,
    )
    r2 = client.responses.create(
        model=MODEL, input=Q2_SEARCH, previous_response_id=r1.id,
    )
    result.response_id = r2.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t06(result: TestResult):
    """previous_response_id、file_search はターン2のみ"""
    client, log = _build_client()
    r1 = client.responses.create(
        model=MODEL, input=Q1_TEXT, store=True,
    )
    r2 = client.responses.create(
        model=MODEL, input=Q2_SEARCH, previous_response_id=r1.id, tools=TOOLS,
    )
    result.response_id = r2.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t07(result: TestResult):
    """Conversations API、ツールなし、2ターン"""
    client, log = _build_client()
    conv = client.conversations.create(metadata={})
    r1 = client.responses.create(
        model=MODEL, input=Q1_TEXT, store=True,
        conversation={"conversation_id": conv.id},
    )
    r2 = client.responses.create(
        model=MODEL, input=Q2_TEXT, store=True,
        conversation={"conversation_id": conv.id},
    )
    result.response_id = r2.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t08(result: TestResult):
    """【既知バグ】Conversations API + file_search、2ターン"""
    client, log = _build_client()
    conv = client.conversations.create(metadata={})
    r1 = client.responses.create(
        model=MODEL, input=Q1_SEARCH, tools=TOOLS, store=True,
        conversation={"conversation_id": conv.id},
    )
    r2 = client.responses.create(
        model=MODEL, input=Q2_SEARCH, tools=TOOLS, store=True,
        conversation={"conversation_id": conv.id},
    )
    result.response_id = r2.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t09(result: TestResult):
    """Client-Managed State、ツールなし、2ターン"""
    client, log = _build_client()
    r1 = client.responses.create(model=MODEL, input=Q1_TEXT)
    history = [
        {"role": "user", "content": Q1_TEXT},
        {"role": "assistant", "content": r1.output_text},
    ]
    r2 = client.responses.create(
        model=MODEL, input=history + [{"role": "user", "content": Q2_TEXT}],
    )
    result.response_id = r2.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t10(result: TestResult):
    """Client-Managed State + file_search、2ターン（回避策）"""
    client, log = _build_client()
    r1 = client.responses.create(model=MODEL, input=Q1_SEARCH, tools=TOOLS)
    history = [
        {"role": "user", "content": Q1_SEARCH},
        {"role": "assistant", "content": r1.output_text},
    ]
    r2 = client.responses.create(
        model=MODEL,
        input=history + [{"role": "user", "content": Q2_SEARCH}],
        tools=TOOLS,
    )
    result.response_id = r2.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t11(result: TestResult):
    """previous_response_id + file_search、3ターン"""
    client, log = _build_client()
    r1 = client.responses.create(
        model=MODEL, input=Q1_SEARCH, tools=TOOLS, store=True,
    )
    try:
        r2 = client.responses.create(
            model=MODEL, input=Q2_SEARCH, previous_response_id=r1.id,
            tools=TOOLS, store=True,
        )
        r3 = client.responses.create(
            model=MODEL, input="それぞれの詳細を教えて",
            previous_response_id=r2.id, tools=TOOLS,
        )
        result.response_id = r3.id
    except Exception:
        raise
    finally:
        result.request_log = log.request_logs
        result.response_log = log.response_logs


def t12(result: TestResult):
    """Client-Managed State（tool call 出力を除外）+ file_search"""
    client, log = _build_client()
    r1 = client.responses.create(model=MODEL, input=Q1_SEARCH, tools=TOOLS)
    # テキストメッセージのみ抽出（file_search_call を除外）
    history = [
        {"role": "user", "content": Q1_SEARCH},
        {"role": "assistant", "content": r1.output_text},
    ]
    r2 = client.responses.create(
        model=MODEL,
        input=history + [{"role": "user", "content": Q2_SEARCH}],
        tools=TOOLS,
    )
    result.response_id = r2.id
    result.request_log = log.request_logs
    result.response_log = log.response_logs


def t13(result: TestResult):
    """previous_response_id + file_search + include パラメータ"""
    client, log = _build_client()
    try:
        r1 = client.responses.create(
            model=MODEL, input=Q1_SEARCH, tools=TOOLS, store=True,
            include=[],
        )
        r2 = client.responses.create(
            model=MODEL, input=Q2_SEARCH, previous_response_id=r1.id, tools=TOOLS,
        )
        result.response_id = r2.id
    except Exception:
        raise
    finally:
        result.request_log = log.request_logs
        result.response_log = log.response_logs


def t14(result: TestResult):
    """previous_response_id + file_search、別モデル"""
    if not ALT_MODEL:
        result.status = "SKIP"
        result.error_message = "GENAI_ALT_MODEL_ID not set"
        return
    client, log = _build_client()
    try:
        r1 = client.responses.create(
            model=ALT_MODEL, input=Q1_SEARCH, tools=TOOLS, store=True,
        )
        r2 = client.responses.create(
            model=ALT_MODEL, input=Q2_SEARCH, previous_response_id=r1.id, tools=TOOLS,
        )
        result.response_id = r2.id
    except Exception:
        raise
    finally:
        result.request_log = log.request_logs
        result.response_log = log.response_logs


def t15(result: TestResult):
    """Conversations API、file_search はターン1のみ"""
    client, log = _build_client()
    conv = client.conversations.create(metadata={})
    r1 = client.responses.create(
        model=MODEL, input=Q1_SEARCH, tools=TOOLS, store=True,
        conversation={"conversation_id": conv.id},
    )
    try:
        r2 = client.responses.create(
            model=MODEL, input=Q2_SEARCH, store=True,
            conversation={"conversation_id": conv.id},
        )
        result.response_id = r2.id
    except Exception:
        raise
    finally:
        result.request_log = log.request_logs
        result.response_log = log.response_logs


def t16(result: TestResult):
    """previous_response_id + file_search、store=False"""
    client, log = _build_client()
    try:
        r1 = client.responses.create(
            model=MODEL, input=Q1_SEARCH, tools=TOOLS, store=False,
        )
        r2 = client.responses.create(
            model=MODEL, input=Q2_SEARCH, previous_response_id=r1.id, tools=TOOLS,
        )
        result.response_id = r2.id
    except Exception:
        raise
    finally:
        result.request_log = log.request_logs
        result.response_log = log.response_logs


# ---------- テスト一覧 ----------
ALL_TESTS = [
    ("T01", "ベースライン: ステートなし、ツールなし", t01),
    ("T02", "ベースライン: ステートなし、file_search", t02),
    ("T03", "prev_resp_id、テキストのみ", t03),
    ("T04", "prev_resp_id + file_search【既知バグ】", t04),
    ("T05", "prev_resp_id、file_search T1のみ", t05),
    ("T06", "prev_resp_id、file_search T2のみ", t06),
    ("T07", "Conversations API、テキストのみ", t07),
    ("T08", "Conversations API + file_search【既知バグ】", t08),
    ("T09", "Client-Managed State、テキストのみ", t09),
    ("T10", "Client-Managed State + file_search", t10),
    ("T11", "prev_resp_id + file_search、3ターン", t11),
    ("T12", "Client-Managed（tool call除外）", t12),
    ("T13", "prev_resp_id + file_search + include=[]", t13),
    ("T14", "prev_resp_id + file_search、別モデル", t14),
    ("T15", "Conversations API、file_search T1のみ", t15),
    ("T16", "prev_resp_id + file_search、store=False", t16),
]


# ---------- レポート生成 ----------
def generate_report(all_results: dict[str, list[TestResult]]):
    now = datetime.now()
    print("=" * 70)
    print("OCI Enterprise AI - file_search + State Management Bug Verification")
    print(f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Region: {REGION} | Model: {MODEL}")
    print(f"Vector Store: {VECTOR_STORE_ID}")
    print("=" * 70)
    print()

    # サマリーテーブル
    print("TEST MATRIX RESULTS")
    print("-" * 70)
    for test_id, desc, _ in ALL_TESTS:
        results = all_results.get(test_id, [])
        if not results:
            continue
        statuses = " ".join(f"{r.status:5s}" for r in results)
        marker = "  <<<" if any(r.status == "FAIL" for r in results) else ""
        print(f"  {test_id:4s}  {desc:42s}  {statuses}{marker}")
    print()

    # エラー詳細
    print("ERROR DETAILS")
    print("-" * 70)
    has_errors = False
    for test_id, desc, _ in ALL_TESTS:
        results = all_results.get(test_id, [])
        for r in results:
            if r.status in ("FAIL", "ERROR"):
                has_errors = True
                msg = r.error_message[:200] if r.error_message else "(no message)"
                print(f"  {r.test_id} run {r.run_number}: [{r.error_type}] {msg}")
    if not has_errors:
        print("  (none)")
    print()

    # 診断分析
    print("DIAGNOSTIC ANALYSIS")
    print("-" * 70)

    def status_of(tid: str) -> str:
        results = all_results.get(tid, [])
        if not results:
            return "N/A"
        fails = sum(1 for r in results if r.status == "FAIL")
        if fails == len(results):
            return "FAIL"
        if fails == 0 and all(r.status in ("PASS", "SKIP") for r in results):
            passes = [r for r in results if r.status == "PASS"]
            return "PASS" if passes else "SKIP"
        return "MIXED"

    t04s = status_of("T04")
    t05s = status_of("T05")
    t06s = status_of("T06")
    t08s = status_of("T08")
    t13s = status_of("T13")
    t14s = status_of("T14")

    if t04s == "FAIL":
        print(f"  T04=FAIL: previous_response_id + file_search でバグ再現を確認")
        if t05s == "FAIL" and t06s == "PASS":
            print("  T05=FAIL + T06=PASS:")
            print("    => サーバーが保存した file_search_call 出力をデシリアライズできない")
            print("    => サーバー側シリアライゼーションバグと断定")
        elif t05s == "PASS":
            print("  T05=PASS:")
            print("    => file_search ツールが turn2 で prev_resp_id と共存できない問題")
        elif t06s == "FAIL":
            print("  T06=FAIL:")
            print("    => prev_resp_id と file_search の組み合わせ自体がバリデーションエラー")
        else:
            print(f"  T05={t05s}, T06={t06s}: 詳細分析が必要")

        if t08s == t04s:
            print(f"  T08={t08s}: Conversations API も同じ → プラットフォームレベルの問題")
        elif t08s != t04s:
            print(f"  T08={t08s}: Conversations API は異なる結果 → 方式固有の問題")

        if t13s == "PASS":
            print(f"  T13=PASS: include パラメータによる回避策あり")
        else:
            print(f"  T13={t13s}: include パラメータでは回避できない")

        if t14s not in ("N/A", "SKIP"):
            if t14s == "PASS":
                print(f"  T14=PASS: 別モデルでは発生しない → モデル固有のバグの可能性")
            else:
                print(f"  T14={t14s}: 別モデルでも同様 → プラットフォーム全体の問題")
    elif t04s == "PASS":
        print("  T04=PASS: 既知バグが再現されず！修正済みの可能性あり")
    else:
        print(f"  T04={t04s}: 結果が混在 → 間欠的な問題の可能性")
    print()

    # JSON 出力
    json_file = f"verify_results_{now.strftime('%Y%m%d_%H%M%S')}.json"
    json_data = {
        "metadata": {
            "date": now.isoformat(),
            "region": REGION,
            "model": MODEL,
            "vector_store_id": VECTOR_STORE_ID,
        },
        "results": {
            tid: [asdict(r) for r in results]
            for tid, results in all_results.items()
        },
    }
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)
    print(f"RAW DATA: {json_file}")
    print()


# ---------- メイン ----------
def main():
    parser = argparse.ArgumentParser(description="file_search + state management bug verification")
    parser.add_argument("--quick", action="store_true", help="各テスト1回のみ")
    parser.add_argument("--test", type=str, help="特定テストのみ実行 (e.g. T04)")
    args = parser.parse_args()

    runs = 1 if args.quick else 3
    tests_to_run = ALL_TESTS

    if args.test:
        target = args.test.upper()
        tests_to_run = [(tid, desc, fn) for tid, desc, fn in ALL_TESTS if tid == target]
        if not tests_to_run:
            print(f"Unknown test: {args.test}", file=sys.stderr)
            print(f"Available: {', '.join(tid for tid, _, _ in ALL_TESTS)}", file=sys.stderr)
            sys.exit(1)

    all_results: dict[str, list[TestResult]] = {}

    total = len(tests_to_run)
    for idx, (test_id, desc, fn) in enumerate(tests_to_run, 1):
        print(f"[{idx}/{total}] {test_id}: {desc} ...", flush=True)
        results = run_test(test_id, desc, fn, runs=runs)
        all_results[test_id] = results
        statuses = " ".join(r.status for r in results)
        print(f"         => {statuses}")
        if idx < total:
            time.sleep(DELAY_BETWEEN_TESTS)

    print()
    generate_report(all_results)


if __name__ == "__main__":
    main()
