"""Streamlit chart helpers."""
import streamlit as st


def line_chart(values, label="Runs"):
    st.line_chart({label: values})
