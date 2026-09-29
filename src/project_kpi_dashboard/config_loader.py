"""Carregamento e validação da configuração da iniciativa (YAML).

Mantém toda a lógica de leitura/validação separada da camada de UI
(``app.py``), facilitando testes unitários e reuso do template.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Chaves obrigatórias no nível raiz do arquivo de configuração.
REQUIRED_TOP_LEVEL_KEYS = ("name", "tagline", "description", "kpis", "pillars", "areas_involved")

# Chaves obrigatórias para cada item de KPI.
REQUIRED_KPI_KEYS = ("name", "value")

# Chaves obrigatórias para cada item de pilar.
REQUIRED_PILLAR_KEYS = ("title", "description")


class ConfigError(ValueError):
    """Erro levantado quando o arquivo de configuração é inválido ou malformado."""


@dataclass(frozen=True)
class Kpi:
    """Representa um indicador (KPI) exibido no dashboard."""

    name: str
    value: str
    delta: str | None = None
    trend: str | None = None  # "up" | "down" | None


@dataclass(frozen=True)
class Pillar:
    """Representa um pilar estratégico da iniciativa."""

    title: str
    description: str


@dataclass(frozen=True)
class InitiativeConfig:
    """Configuração completa de uma iniciativa, pronta para renderização."""

    name: str
    tagline: str
    description: str
    kpis: list[Kpi] = field(default_factory=list)
    pillars: list[Pillar] = field(default_factory=list)
    areas_involved: list[str] = field(default_factory=list)


def _require_keys(data: dict[str, Any], required: tuple[str, ...], context: str) -> None:
    missing = [key for key in required if key not in data]
    if missing:
        raise ConfigError(
            f"Configuração inválida em '{context}': chave(s) obrigatória(s) ausente(s): "
            f"{', '.join(missing)}."
        )


def _parse_kpis(raw_kpis: Any) -> list[Kpi]:
    if raw_kpis is None:
        return []
    if not isinstance(raw_kpis, list):
        raise ConfigError("A chave 'kpis' deve ser uma lista.")

    kpis: list[Kpi] = []
    for idx, item in enumerate(raw_kpis):
        if not isinstance(item, dict):
            raise ConfigError(f"O item de KPI no índice {idx} deve ser um mapeamento (dict).")
        _require_keys(item, REQUIRED_KPI_KEYS, context=f"kpis[{idx}]")
        kpis.append(
            Kpi(
                name=str(item["name"]),
                value=str(item["value"]),
                delta=str(item["delta"]) if item.get("delta") is not None else None,
                trend=item.get("trend"),
            )
        )
    return kpis


def _parse_pillars(raw_pillars: Any) -> list[Pillar]:
    if raw_pillars is None:
        return []
    if not isinstance(raw_pillars, list):
        raise ConfigError("A chave 'pillars' deve ser uma lista.")

    pillars: list[Pillar] = []
    for idx, item in enumerate(raw_pillars):
        if not isinstance(item, dict):
            raise ConfigError(f"O item de pilar no índice {idx} deve ser um mapeamento (dict).")
        _require_keys(item, REQUIRED_PILLAR_KEYS, context=f"pillars[{idx}]")
        pillars.append(Pillar(title=str(item["title"]), description=str(item["description"])))
    return pillars


def _parse_areas(raw_areas: Any) -> list[str]:
    if raw_areas is None:
        return []
    if not isinstance(raw_areas, list):
        raise ConfigError("A chave 'areas_involved' deve ser uma lista.")
    return [str(area) for area in raw_areas]


def parse_config(data: dict[str, Any]) -> InitiativeConfig:
    """Valida e converte um dicionário bruto em um :class:`InitiativeConfig`.

    Levanta :class:`ConfigError` com mensagem clara caso alguma chave
    obrigatória esteja ausente ou os tipos estejam incorretos.
    """
    if not isinstance(data, dict):
        raise ConfigError("O conteúdo do arquivo de configuração deve ser um mapeamento (YAML/JSON de objeto).")

    _require_keys(data, REQUIRED_TOP_LEVEL_KEYS, context="raiz do arquivo")

    return InitiativeConfig(
        name=str(data["name"]),
        tagline=str(data["tagline"]),
        description=str(data["description"]),
        kpis=_parse_kpis(data.get("kpis")),
        pillars=_parse_pillars(data.get("pillars")),
        areas_involved=_parse_areas(data.get("areas_involved")),
    )


def load_config(path: str | Path) -> InitiativeConfig:
    """Lê um arquivo YAML de configuração e retorna um :class:`InitiativeConfig` validado.

    :param path: Caminho para o arquivo YAML.
    :raises ConfigError: se o arquivo não existir, não puder ser parseado
        como YAML, ou não contiver as chaves obrigatórias.
    """
    file_path = Path(path)
    logger.info("Carregando configuração da iniciativa de '%s'.", file_path)

    if not file_path.exists():
        raise ConfigError(f"Arquivo de configuração não encontrado: '{file_path}'.")

    try:
        raw_text = file_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"Não foi possível ler o arquivo '{file_path}': {exc}") from exc

    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"O arquivo '{file_path}' contém YAML malformado: {exc}") from exc

    if data is None:
        raise ConfigError(f"O arquivo '{file_path}' está vazio.")

    config = parse_config(data)
    logger.info(
        "Configuração carregada: %d KPI(s), %d pilar(es), %d área(s).",
        len(config.kpis),
        len(config.pillars),
        len(config.areas_involved),
    )
    return config
