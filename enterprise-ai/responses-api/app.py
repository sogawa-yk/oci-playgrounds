"""OCI Enterprise AI - 資料検索・解説エージェント

ベクトルストアに登録済みの PDF を Responses API の file_search で検索し、
質問に回答するエージェント。短期メモリの ON/OFF を Chat Profile で切り替え可能。

メモリ ON 時は Client-Managed State で会話履歴をクライアント側に保持する。
※ file_search 使用時は previous_response_id / Conversations API が
  json_parse_error になるため、この方式を採用。
"""

from __future__ import annotations

import asyncio
import os

import chainlit as cl
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
INSTRUCTIONS = (
    "You are answering questions only from the uploaded PDF files in the vector store. "
    "Use file_search results as the primary evidence. "
    "If the retrieved content is insufficient, say so explicitly."
)
TOOLS = [{"type": "file_search", "vector_store_ids": [VECTOR_STORE_ID]}]


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


def _build_client() -> OpenAI:
    region = os.environ.get("OCI_REGION", "ap-osaka-1")
    return OpenAI(
        base_url=f"https://inference.generativeai.{region}.oci.oraclecloud.com/openai/v1",
        api_key="not-used",
        project=os.environ["OCI_GENAI_PROJECT"],
        http_client=httpx.Client(auth=_build_auth()),
    )


# ---------- Responses API 呼び出し ----------
def search(question: str, history: list[dict] | None = None) -> dict:
    """Responses API を呼び出し、回答・ソースを返す。"""
    client = _build_client()

    # Client-Managed State: 会話履歴があれば input にメッセージ配列を渡す
    if history:
        input_data = history + [{"role": "user", "content": question}]
    else:
        input_data = question

    response = client.responses.create(
        model=MODEL,
        input=input_data,
        instructions=INSTRUCTIONS,
        tools=TOOLS,
    )

    # ソースファイル名を収集
    sources = []
    for item in response.output:
        if getattr(item, "type", None) == "file_search_call":
            for r in getattr(item, "results", None) or []:
                name = getattr(r, "filename", None)
                if name and name not in sources:
                    sources.append(name)

    return {
        "answer": response.output_text,
        "sources": sources,
    }


# ---------- Chainlit UI ----------
@cl.set_chat_profiles
async def chat_profiles():
    return [
        cl.ChatProfile(
            name="memory-on",
            markdown_description="会話履歴を保持します（Client-Managed State）",
        ),
        cl.ChatProfile(
            name="memory-off",
            markdown_description="各質問を独立して処理します",
        ),
    ]


def _is_memory_enabled() -> bool:
    return cl.user_session.get("chat_profile") != "memory-off"


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history", [])
    mode = "ON - 会話の文脈を保持します" if _is_memory_enabled() else "OFF - 各質問を独立して処理します"
    await cl.Message(
        content=f"## 資料検索・解説エージェント\n\nベクトルストアに登録済みの PDF について質問できます。\n\n**短期メモリ: {mode}**"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    memory = _is_memory_enabled()
    history = cl.user_session.get("history") if memory else None

    waiting = cl.Message(content="検索中...")
    await waiting.send()

    try:
        result = await asyncio.to_thread(search, message.content, history)
    except Exception as exc:
        waiting.content = f"エラー: {exc}"
        await waiting.update()
        return

    # メモリモード: 会話履歴を更新
    if memory:
        history = cl.user_session.get("history") or []
        history.append({"role": "user", "content": message.content})
        history.append({"role": "assistant", "content": result["answer"]})
        cl.user_session.set("history", history)

    # 回答を組み立て
    parts = [result["answer"]]
    if result["sources"]:
        parts.append("\n**Sources**")
        parts.extend(f"- {s}" for s in result["sources"])
    parts.append(f"\n`memory: {'on' if memory else 'off'}`")

    waiting.content = "\n".join(parts)
    await waiting.update()
