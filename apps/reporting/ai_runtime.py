from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from multiprocessing import cpu_count

import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize


@dataclass(frozen=True)
class RuntimeProfile:
    cpu_count: int
    cpu_target: float
    worker_threads: int
    device: str
    gpu_name: str | None
    embedding_model: str


def _bounded_cpu_target(raw: str) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        value = 0.75
    return min(max(value, 0.2), 1.0)


@lru_cache(maxsize=1)
def get_runtime_profile() -> RuntimeProfile:
    total_cpu = max(1, cpu_count())
    target = _bounded_cpu_target(os.getenv("OFFICE_CPU_TARGET", "0.75"))
    workers = max(1, int(total_cpu * target))

    os.environ.setdefault("OMP_NUM_THREADS", str(workers))
    os.environ.setdefault("MKL_NUM_THREADS", str(workers))
    os.environ.setdefault("NUMEXPR_MAX_THREADS", str(workers))

    device = "cpu"
    gpu_name = None
    try:
        import torch

        torch.set_num_threads(workers)
        interop = max(1, workers // 2)
        torch.set_num_interop_threads(interop)
        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
    except Exception:
        device = "cpu"
        gpu_name = None
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=2,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                device = "cuda"
                gpu_name = result.stdout.splitlines()[0].strip()
        except Exception:
            pass

    model_name = os.getenv("OFFICE_EMBED_MODEL", "nltk-frequency")
    return RuntimeProfile(
        cpu_count=total_cpu,
        cpu_target=target,
        worker_threads=workers,
        device=device,
        gpu_name=gpu_name,
        embedding_model=model_name,
    )


_EMBEDDER = None


def get_embedder():
    global _EMBEDDER
    if _EMBEDDER is not None:
        return _EMBEDDER

    profile = get_runtime_profile()
    try:
        from sentence_transformers import SentenceTransformer

        _EMBEDDER = SentenceTransformer(
            profile.embedding_model,
            device="cuda" if profile.device == "cuda" else "cpu",
        )
    except Exception:
        _EMBEDDER = None
    return _EMBEDDER


def semantic_key_points(text: str, max_points: int = 8) -> list[str]:
    try:
        sentences = [s.strip() for s in sent_tokenize(text) if s.strip()]
    except Exception:
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]
    if len(sentences) <= max_points:
        return sentences

    model = get_embedder()
    if model is None:
        return _frequency_rank_sentences(sentences, max_points)

    try:
        vectors = model.encode(sentences, normalize_embeddings=True)
        centroid = np.mean(vectors, axis=0)
        scores = np.dot(vectors, centroid)
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)[: max_points * 2]
        top_idx = sorted({idx for idx, _ in ranked})[:max_points]
        return [sentences[idx] for idx in top_idx]
    except Exception:
        return _frequency_rank_sentences(sentences, max_points)


def _frequency_rank_sentences(sentences: list[str], max_points: int) -> list[str]:
    try:
        stop_words = set(stopwords.words("english"))
    except Exception:
        stop_words = set()

    frequency = {}
    for sentence in sentences:
        for token in word_tokenize(sentence.lower()):
            if not token.isalpha() or token in stop_words:
                continue
            frequency[token] = frequency.get(token, 0) + 1

    scored = []
    for idx, sentence in enumerate(sentences):
        score = 0
        for token in word_tokenize(sentence.lower()):
            if token in frequency:
                score += frequency[token]
        scored.append((idx, score))

    top = sorted(scored, key=lambda item: item[1], reverse=True)[: max_points * 2]
    selected_idx = sorted({idx for idx, _ in top})[:max_points]
    return [sentences[idx] for idx in selected_idx]
