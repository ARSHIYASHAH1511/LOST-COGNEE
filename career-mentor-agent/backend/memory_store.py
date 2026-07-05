import inspect
import json
import logging
import os
from pathlib import Path
from typing import Any

try:
    import cognee  # type: ignore
except Exception as exc:  # pragma: no cover - exercised when dependency is missing
    cognee = None
    _COGNEE_IMPORT_ERROR = exc
else:
    _COGNEE_IMPORT_ERROR = None

log = logging.getLogger(__name__)

DEFAULT_MEMORY_FILE = Path(__file__).resolve().parent / "data" / "chat_memory.json"


def get_memory_file() -> Path:
    configured_path = os.getenv("CHAT_MEMORY_FILE")
    if configured_path:
        return Path(configured_path).expanduser().resolve()
    return DEFAULT_MEMORY_FILE


def _load_memory_store(path: Path | None = None) -> dict[str, dict[str, Any]]:
    target_path = path or get_memory_file()
    if not target_path.exists():
        return {}

    try:
        with target_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception as exc:  # pragma: no cover - defensive
        log.warning("Could not read chat memory store %s: %s", target_path, exc)
        return {}


def _save_memory_store(store: dict[str, dict[str, Any]], path: Path | None = None) -> None:
    target_path = path or get_memory_file()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(store, handle, indent=2, ensure_ascii=False)
    tmp_path.replace(target_path)


async def configure_cognee(
    llm_provider: str,
    llm_model: str,
    llm_api_key: str,
    embedding_provider: str,
    embedding_model: str,
    embedding_api_key: str,
) -> None:
    if cognee is None:
        log.warning(
            "Cognee is not available in this environment; chat memory will be stored locally in %s",
            get_memory_file(),
        )
        return

    try:
        if hasattr(cognee, "config") and hasattr(cognee.config, "set_llm_config"):
            cognee.config.set_llm_config(
                {
                    "llm_provider": llm_provider,
                    "llm_model": llm_model,
                    "llm_api_key": llm_api_key,
                }
            )
    except Exception as exc:  # pragma: no cover - defensive
        log.warning("Cognee LLM config skipped: %s", exc)

    try:
        if hasattr(cognee, "config") and hasattr(cognee.config, "set_embedding_config"):
            cognee.config.set_embedding_config(
                {
                    "embedding_provider": embedding_provider,
                    "embedding_model": embedding_model,
                    "embedding_api_key": embedding_api_key,
                }
            )
    except Exception as exc:  # pragma: no cover - defensive
        log.warning("Cognee embedding config skipped: %s", exc)


async def recall_memories(user_id: str, query: str) -> str:
    if cognee is not None:
        try:
            result = cognee.recall(query, datasets=[user_id])
            if inspect.isawaitable(result):
                result = await result

            if not result:
                return ""

            memory_lines: list[str] = []
            for item in result[:8]:
                text = getattr(item, "text", None) or getattr(item, "content", None) or str(item)
                if text and text.strip():
                    memory_lines.append(text.strip())

            if memory_lines:
                return "\n".join(memory_lines)
        except Exception as exc:  # pragma: no cover - defensive
            log.warning("Cognee recall failed for user %s: %s", user_id, exc)

    store = _load_memory_store()
    user_messages = store.get(user_id, {}).get("messages", [])
    if not user_messages:
        return ""

    query_terms = {term.lower() for term in query.split() if len(term) > 2}
    relevant: list[str] = []
    for entry in reversed(user_messages[-10:]):
        content = str(entry.get("content", "")).strip()
        if not content:
            continue

        if not query_terms or any(term in content.lower() for term in query_terms):
            role = "User" if entry.get("role") == "user" else "Assistant"
            relevant.append(f"{role}: {content}")
            if len(relevant) >= 8:
                break

    return "\n".join(reversed(relevant))


async def store_memory(user_id: str, user_msg: str, bot_reply: str) -> None:
    store = _load_memory_store()
    user_store = store.setdefault(user_id, {"messages": []})
    user_store.setdefault("messages", []).extend(
        [
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": bot_reply},
        ]
    )
    user_store["updated_at"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
    _save_memory_store(store)

    if cognee is None:
        return

    text_to_store = f"User said: {user_msg}\nCareer Mentor replied: {bot_reply}"
    try:
        for method_name, kwargs in (("remember", {"dataset_name": user_id}), ("add", {"dataset_name": user_id}), ("remember", {"datasets": [user_id]})):
            if not hasattr(cognee, method_name):
                continue
            try:
                result = getattr(cognee, method_name)(text_to_store, **kwargs)
                if inspect.isawaitable(result):
                    await result
                log.info("Cognee memory stored for user %s", user_id)
                return
            except TypeError:
                continue
            except Exception as exc:  # pragma: no cover - defensive
                log.warning("Cognee memory store failed for user %s: %s", user_id, exc)
                return
    except Exception as exc:  # pragma: no cover - defensive
        log.warning("Cognee memory store failed for user %s: %s", user_id, exc)
