"""Foundry Local etrafında sarmalayıcı: daemon'ın ve gerekli modellerin
çalıştığından emin olur, sonra yerel OpenAI-uyumlu uç nokta üzerinden basit
chat() ve embed() çağrıları sunar. Modeller indirildikten sonra bulut
hesabı ya da ağ çağrısı gerekmez.

Bu, `foundry` CLI'ına doğrudan konuşur (server status/start, model
download/load/info) -- foundry-local-sdk üzerinden değil: SDK'nın REST
istemcisi, kurulu Foundry Local sunucu sürümüyle eşleşmeyen uç nokta
yollarını (ör. `/foundry/list`) hedefliyor; CLI'ın JSON çıktısı
(`-o json`) ise stabil ve ayrıştırması kolay.
"""
import json
import subprocess

from openai import OpenAI

DOWNLOAD_TIMEOUT_SECONDS = 1800
LOAD_TIMEOUT_SECONDS = 300


def _run(*args, timeout=60):
    # foundry CLI, konsolun aktif kod sayfası ne olursa olsun UTF-8 ilerleme
    # çıktısı (kutu-çizim/unicode karakterleri) yazıyor, bu yüzden yerel
    # ayara güvenmek yerine açıkça UTF-8 olarak decode ediyoruz.
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

    def chat(self, system_prompt, user_prompt, max_tokens=800):
        response = self._client.chat.completions.create(
            model=self._chat_model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
