"""Wrapper around Foundry Local: ensures the daemon and required models are
running, then exposes simple chat() and embed() calls via the local
OpenAI-compatible endpoint. No cloud account or network calls are required
once models are downloaded.

This talks to the `foundry` CLI directly (server status/start, model
download/load/info) rather than through foundry-local-sdk: the SDK's REST
client targets endpoint paths (e.g. `/foundry/list`) that don't match the
currently installed Foundry Local server version, while the CLI's JSON
output (`-o json`) is stable and easy to parse.
"""
import json
import subprocess

from openai import OpenAI

DOWNLOAD_TIMEOUT_SECONDS = 1800
LOAD_TIMEOUT_SECONDS = 300


def _run(*args, timeout=60):
    # The foundry CLI writes UTF-8 progress output (box-drawing/unicode
    # glyphs) regardless of the console's active code page, so decode as
    # UTF-8 explicitly instead of relying on the locale default.
    return subprocess.run(
        ["foundry", *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=True,
    )


def _run_json(*args, timeout=60):
    result = _run(*args, "-o", "json", timeout=timeout)
    return json.loads(result.stdout)


def _ensure_server_running():
    status = _run_json("server", "status")
    if not status.get("running"):
        _run("server", "start", timeout=120)
        status = _run_json("server", "status")
    return status["webUrls"][0]


def _ensure_model_ready(alias):
    _run("model", "download", alias, timeout=DOWNLOAD_TIMEOUT_SECONDS)
    _run("model", "load", alias, timeout=LOAD_TIMEOUT_SECONDS)
    info = _run_json("model", "info", alias)
    return info["model"]["id"]


class FoundryClient:
    def __init__(self, chat_alias, embedding_alias):
        base_url = f"{_ensure_server_running()}/v1"

        self._chat_model_id = _ensure_model_ready(chat_alias)
        self._embed_model_id = _ensure_model_ready(embedding_alias)

        self._client = OpenAI(base_url=base_url, api_key="not-needed")

    def embed(self, texts):
        response = self._client.embeddings.create(
            model=self._embed_model_id,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def chat(self, system_prompt, user_prompt):
        response = self._client.chat.completions.create(
            model=self._chat_model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
