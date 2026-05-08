from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st


@dataclass(frozen=True)
class ApiConfig:
    base_url: str


def api_config() -> ApiConfig:
    base = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    return ApiConfig(base_url=base)


def _inject_css():
    st.markdown(
        """
<style>
  .app-title { font-size: 1.8rem; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 0.25rem; }
  .app-subtitle { color: #6b7280; margin-top: 0; }
  .card {
    background: rgba(255,255,255,0.60);
    border: 1px solid rgba(148,163,184,0.35);
    border-radius: 18px;
    padding: 18px 18px;
    box-shadow: 0 10px 30px rgba(2,6,23,0.06);
  }
  .metric-big { font-size: 2.1rem; font-weight: 800; }
  .muted { color: #6b7280; font-size: 0.95rem; }
  .pill {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    border: 1px solid rgba(148,163,184,0.35);
    background: rgba(241,245,249,0.70);
    font-size: 0.85rem;
    margin-right: 6px;
  }
</style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(ttl=60)
def fetch_crops(base_url: str) -> list[str]:
    r = requests.get(f"{base_url}/crops", timeout=10)
    r.raise_for_status()
    payload = r.json()
    return payload.get("crops", [])


def fetch_historical(base_url: str, crop_name: str, start_year: str, end_year: str) -> pd.DataFrame:
    r = requests.get(
        f"{base_url}/historical-data",
        params={"crop_name": crop_name, "start_year": start_year, "end_year": end_year},
        timeout=20,
    )
    r.raise_for_status()
    points = r.json().get("points", [])
    df = pd.DataFrame(points)
    return df


def predict(base_url: str, crop_name: str, rainfall: float, avg_temperature: float) -> dict[str, Any]:
    r = requests.post(
        f"{base_url}/predict",
        json={
            "crop_name": crop_name,
            "rainfall": float(rainfall),
            "avg_temperature": float(avg_temperature),
        },
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def _line_chart(df: pd.DataFrame, x: str, y: str, title: str, y_label: str):
    plot_df = df.copy()
    if "year_end" in plot_df.columns:
        plot_df = plot_df.sort_values("year_end")
    elif "year_start" in plot_df.columns:
        plot_df = plot_df.sort_values("year_start")

    x_col = "year_end" if "year_end" in plot_df.columns else x
    x_order = plot_df[x].astype(str).tolist()
    fig = px.line(
        plot_df,
        x=x_col,
        y=y,
        markers=True,
        title=title,
        template="plotly_white",
        hover_data={"fiscal_year": True, y: True},
    )
    fig.update_layout(
        title=dict(x=0.01, xanchor="left"),
        margin=dict(l=10, r=10, t=60, b=10),
        height=360,
    )
    if x_col == "year_end":
        fig.update_xaxes(
            title_text="Fiscal Year End",
            tickmode="linear",
            dtick=1,
        )
    else:
        fig.update_xaxes(
            title_text="Fiscal Year",
            type="category",
            categoryorder="array",
            categoryarray=x_order,
            tickangle=-45,
        )
    fig.update_yaxes(title_text=y_label)
    st.plotly_chart(fig, use_container_width=True)


def _fiscal_start_year(fiscal_year: str) -> int | None:
    if not isinstance(fiscal_year, str):
        return None
    token = fiscal_year[:4]
    return int(token) if token.isdigit() else None


def _fiscal_end_year(fiscal_year: str) -> int | None:
    """
    Convert labels like:
      1981-82 -> 1982
      1999-00 -> 2000
      2023-24 -> 2024
    """
    if not isinstance(fiscal_year, str) or "-" not in fiscal_year:
        return None
    start = _fiscal_start_year(fiscal_year)
    if start is None:
        return None
    suffix = fiscal_year.split("-")[-1].strip()
    if len(suffix) != 2 or not suffix.isdigit():
        return None
    end = (start // 100) * 100 + int(suffix)
    if end < start:
        end += 100
    return end


def _prepare_year_filtered_df(
    df_raw: pd.DataFrame, start_end_year: int, end_end_year: int
) -> pd.DataFrame:
    df = df_raw.copy()
    df["year_end"] = df["fiscal_year"].apply(_fiscal_end_year)
    df = df[df["year_end"].notna()]
    df = df[
        (df["year_end"] >= int(start_end_year))
        & (df["year_end"] <= int(end_end_year))
    ].sort_values("year_end")
    return df


def main():
    st.set_page_config(
        page_title="Agri Crop Analytics",
        page_icon="🌾",
        layout="wide",
    )
    _inject_css()

    cfg = api_config()

    st.markdown('<div class="app-title">Agricultural Crop Analysis & Production Prediction</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="app-subtitle">Backend API: <span class="pill">{cfg.base_url}</span></div>',
        unsafe_allow_html=True,
    )

    try:
        crops = fetch_crops(cfg.base_url)
    except Exception as e:
        st.error(f"Failed to reach API. Start the backend first. Details: {e}")
        st.stop()

    if not crops:
        st.warning("No crops found in database.")
        st.stop()

    tab1, tab2 = st.tabs(["Historical Analysis Dashboard", "Production Prediction Dashboard"])

    with tab1:
        st.markdown("### Historical Analysis Dashboard")
        with st.container():
            crop = st.selectbox("Crop", crops, index=0, key="hist_crop")

        try:
            # Pull complete crop history once, then drive slider + charts from actual years.
            df_all = fetch_historical(cfg.base_url, crop, "1900", "2100")
        except requests.HTTPError as e:
            st.error(f"Failed to fetch historical data: {e.response.text if e.response is not None else e}")
            st.stop()
        except Exception as e:
            st.error(f"Failed to fetch historical data: {e}")
            st.stop()

        if df_all.empty:
            st.info("No historical data returned for this crop.")
            st.stop()

        all_years = [_fiscal_end_year(v) for v in df_all["fiscal_year"].tolist()]
        all_years = [y for y in all_years if y is not None]
        if not all_years:
            st.info("No valid fiscal-year values found for this crop.")
            st.stop()

        year_min = min(all_years)
        year_max = max(all_years)

        slider_key = "hist_year_slider"
        reset = st.button("Reset to full range", key="reset_hist_range")
        if reset:
            st.session_state[slider_key] = (year_min, year_max)

        # Keep previous selection if present, but clamp it to current crop's bounds.
        default_range = (year_min, year_max)
        if slider_key in st.session_state:
            try:
                prev_start, prev_end = st.session_state[slider_key]
                default_range = (
                    max(year_min, int(prev_start)),
                    min(year_max, int(prev_end)),
                )
                if default_range[0] > default_range[1]:
                    default_range = (year_min, year_max)
            except Exception:
                default_range = (year_min, year_max)

        year_range = st.slider(
            "Fiscal year end (derived from values like '1981-82' -> 1982)",
            min_value=year_min,
            max_value=year_max,
            value=default_range,
            step=1,
            key=slider_key,
        )

        df = _prepare_year_filtered_df(df_all, year_range[0], year_range[1])

        if df.empty:
            st.info("No data returned for selected filters.")
            st.stop()

        st.caption(
            f"Showing {len(df)} records for {crop} from {year_range[0]} to {year_range[1]} "
            f"(available data for this crop: {year_min} to {year_max})."
        )
        st.caption(
            f"Latest fiscal year visible in graph: {df['fiscal_year'].iloc[-1]}"
        )

        st.markdown('<div class="card">', unsafe_allow_html=True)
        _line_chart(df, "fiscal_year", "rainfall", "Rainfall Trend", "Rainfall")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        _line_chart(df, "fiscal_year", "avg_temperature", "Avg Temperature Trend", "Avg Temperature")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        _line_chart(df, "fiscal_year", "production", "Crop Production Trend", "Production")
        st.markdown("</div>", unsafe_allow_html=True)

        # 100% Stacked Chart for Rainfall, Avg Temp, and Production
        st.markdown('<div class="card">', unsafe_allow_html=True)
        # Normalize values to percentages
        df_normalized = df.copy()
        df_normalized['total'] = df_normalized['rainfall'] + df_normalized['avg_temperature'] + df_normalized['production']
        df_normalized['rainfall_pct'] = (df_normalized['rainfall'] / df_normalized['total']) * 100
        df_normalized['avg_temperature_pct'] = (df_normalized['avg_temperature'] / df_normalized['total']) * 100
        df_normalized['production_pct'] = (df_normalized['production'] / df_normalized['total']) * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_normalized['fiscal_year'], 
            y=df_normalized['rainfall_pct'], 
            mode='lines', 
            name='Rainfall (%)', 
            stackgroup='one'
        ))
        fig.add_trace(go.Scatter(
            x=df_normalized['fiscal_year'], 
            y=df_normalized['avg_temperature_pct'], 
            mode='lines', 
            name='Avg Temperature (%)', 
            stackgroup='one'
        ))
        fig.add_trace(go.Scatter(
            x=df_normalized['fiscal_year'], 
            y=df_normalized['production_pct'], 
            mode='lines', 
            name='Production (%)', 
            stackgroup='one'
        ))
        fig.update_layout(
            title='100% Stacked Line Chart: Rainfall, Avg Temperature, and Production',
            xaxis_title='Fiscal Year',
            yaxis_title='Percentage (%)',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("### Production Prediction Dashboard")
        left, right = st.columns([2, 3])

        with left:
            crop2 = st.selectbox("Crop", crops, index=0, key="pred_crop")
            rainfall = st.number_input("Rainfall", min_value=0.0, value=200.0, step=1.0)
            temp = st.number_input("Average temperature", min_value=-20.0, max_value=60.0, value=25.0, step=0.1)
            do_pred = st.button("Predict", type="primary", use_container_width=True)

        with right:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="muted">Prediction Result</div>', unsafe_allow_html=True)
            if do_pred:
                with st.spinner("Running model..."):
                    try:
                        res = predict(cfg.base_url, crop2, rainfall, temp)
                        pred_val = res.get("predicted_production")
                        st.markdown(f'<div class="metric-big">{pred_val:.4f} tons/ha</div>', unsafe_allow_html=True)
                        st.markdown('<div class="muted">Unit: tons per hectare</div>', unsafe_allow_html=True)
                        st.markdown(
                            f'<div class="muted">Crop: <b>{crop2}</b> · Features: rainfall={rainfall}, avg_temperature={temp}</div>',
                            unsafe_allow_html=True,
                        )
                        if "model_file" in res and "scaler_file" in res:
                            st.caption(f"Loaded: {res['model_file']} + {res['scaler_file']}")
                    except requests.HTTPError as e:
                        st.error(f"Prediction failed: {e.response.text if e.response is not None else e}")
                    except Exception as e:
                        st.error(f"Prediction failed: {e}")
            else:
                st.markdown('<div class="muted">Select a crop, enter weather inputs, then click Predict.</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

