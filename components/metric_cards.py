"""Render a row of metric cards."""
import streamlit as st


def render_metrics(metrics):
    columns = st.columns(len(metrics))
    for column, (label, value) in zip(columns, metrics.items()):
        column.metric(label, value)
