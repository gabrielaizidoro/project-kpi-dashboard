"""Dashboard Streamlit (template) para status de uma iniciativa interna.

Este app é um TEMPLATE de portfólio: todo o conteúdo exibido por padrão
(``config/initiative_example.yaml``) é fictício. Para reutilizar, edite o
YAML apontado por ``CONFIG_PATH`` ou escolha outro arquivo pela sidebar.
"""

from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

from project_kpi_dashboard.config_loader import ConfigError, InitiativeConfig, load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "initiative_example.yaml"

TREND_ICONS = {"up": "🟢 ▲", "down": "🔴 ▼"}


def render_header(config: InitiativeConfig) -> None:
    """Renderiza o cabeçalho com nome e descrição curta da iniciativa."""
    st.title(config.name)
    st.caption(config.tagline)
    st.write(config.description)


def render_kpis(config: InitiativeConfig) -> None:
    """Renderiza a linha de cartões de KPI."""
    st.subheader("Indicadores-chave (KPIs)")
    if not config.kpis:
        st.info("Nenhum KPI configurado.")
        return

    columns = st.columns(len(config.kpis))
    for column, kpi in zip(columns, config.kpis):
        label = kpi.name
        if kpi.trend in TREND_ICONS:
            label = f"{TREND_ICONS[kpi.trend]} {label}"
        column.metric(label=label, value=kpi.value, delta=kpi.delta)


def render_kpi_chart(config: InitiativeConfig) -> None:
    """Renderiza um gráfico de barras simples resumindo os KPIs numéricos."""
    numeric_kpis = []
    for kpi in config.kpis:
        cleaned = "".join(ch for ch in kpi.value if ch.isdigit() or ch in ".,-").replace(",", ".")
        try:
            numeric_kpis.append((kpi.name, float(cleaned)))
        except ValueError:
            continue

    if not numeric_kpis:
        return

    st.subheader("Visão geral dos KPIs (numéricos)")
    chart_data = {name: value for name, value in numeric_kpis}
    st.bar_chart(chart_data)


def render_pillars(config: InitiativeConfig) -> None:
    """Renderiza a seção de pilares estratégicos em colunas."""
    st.subheader("Pilares estratégicos")
    if not config.pillars:
        st.info("Nenhum pilar configurado.")
        return

    columns = st.columns(len(config.pillars))
    for column, pillar in zip(columns, config.pillars):
        with column:
            st.markdown(f"**{pillar.title}**")
            st.write(pillar.description)


def render_areas(config: InitiativeConfig) -> None:
    """Renderiza a lista de áreas/times envolvidos como badges simples."""
    st.subheader("Áreas envolvidas")
    if not config.areas_involved:
        st.info("Nenhuma área configurada.")
        return

    st.markdown(" &nbsp; ".join(f"`{area}`" for area in config.areas_involved))


def load_config_from_sidebar() -> InitiativeConfig | None:
    """Permite escolher/informar o caminho do YAML de configuração pela sidebar."""
    st.sidebar.header("Configuração")
    config_path_str = st.sidebar.text_input("Caminho do arquivo YAML", value=str(DEFAULT_CONFIG_PATH))

    try:
        return load_config(config_path_str)
    except ConfigError as exc:
        logger.error("Falha ao carregar configuração: %s", exc)
        st.error(f"Erro ao carregar configuração: {exc}")
        return None


def main() -> None:
    """Ponto de entrada do dashboard Streamlit."""
    st.set_page_config(page_title="Dashboard de Status de Iniciativa (Template)", layout="wide")

    st.sidebar.info(
        "Este é um template de portfólio. Todo o conteúdo de exemplo "
        "(nomes, KPIs, pilares) é fictício."
    )

    config = load_config_from_sidebar()
    if config is None:
        st.stop()

    render_header(config)
    st.divider()
    render_kpis(config)
    render_kpi_chart(config)
    st.divider()
    render_pillars(config)
    st.divider()
    render_areas(config)


if __name__ == "__main__":
    main()
