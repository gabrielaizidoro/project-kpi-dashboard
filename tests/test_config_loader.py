"""Testes unitários para project_kpi_dashboard.config_loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from project_kpi_dashboard.config_loader import ConfigError, load_config

VALID_YAML = """
name: "Iniciativa Teste"
tagline: "Uma tagline de teste."
description: "Descrição de teste."
kpis:
  - name: "Métrica A"
    value: "10"
    delta: "+1"
    trend: "up"
pillars:
  - title: "Pilar 1"
    description: "Descrição do pilar 1."
areas_involved:
  - "Time A"
  - "Time B"
"""

MISSING_KEY_YAML = """
name: "Iniciativa Teste"
tagline: "Uma tagline de teste."
description: "Descrição de teste."
kpis: []
pillars: []
"""

EMPTY_PILLARS_YAML = """
name: "Iniciativa Teste"
tagline: "Uma tagline de teste."
description: "Descrição de teste."
kpis:
  - name: "Métrica A"
    value: "10"
pillars: []
areas_involved: []
"""

MALFORMED_YAML = """
name: "Iniciativa Teste
  tagline: [unclosed
"""


def _write_yaml(tmp_path: Path, content: str, filename: str = "config.yaml") -> Path:
    file_path = tmp_path / filename
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_valid_config_loads_correctly(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path, VALID_YAML)

    config = load_config(path)

    assert config.name == "Iniciativa Teste"
    assert config.tagline == "Uma tagline de teste."
    assert len(config.kpis) == 1
    assert config.kpis[0].name == "Métrica A"
    assert config.kpis[0].value == "10"
    assert config.kpis[0].trend == "up"
    assert len(config.pillars) == 1
    assert config.pillars[0].title == "Pilar 1"
    assert config.areas_involved == ["Time A", "Time B"]


def test_missing_required_key_raises_clear_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path, MISSING_KEY_YAML)

    with pytest.raises(ConfigError) as exc_info:
        load_config(path)

    assert "areas_involved" in str(exc_info.value)


def test_empty_pillars_list_handled_gracefully(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path, EMPTY_PILLARS_YAML)

    config = load_config(path)

    assert config.pillars == []
    assert len(config.kpis) == 1


def test_malformed_yaml_raises_clear_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path, MALFORMED_YAML)

    with pytest.raises(ConfigError) as exc_info:
        load_config(path)

    assert "malformado" in str(exc_info.value).lower()


def test_missing_file_raises_clear_error(tmp_path: Path) -> None:
    missing_path = tmp_path / "does_not_exist.yaml"

    with pytest.raises(ConfigError) as exc_info:
        load_config(missing_path)

    assert "não encontrado" in str(exc_info.value).lower()
