"""
Dasbor Interaktif Pemantauan Operasional & Prediksi Stok — Kopi Sewu Batam
Tim Capstone Asah 2026: A26-CS267 (Karsa) — Divisi Data Science

Cakupan Side Quest DS #1 (Dasbor untuk Memantau Bisnis):
- Indikator bisnis (KPI) lengkap & filter interaktif (tanggal, armada, lokasi, cuaca, tipe hari, kategori)
- Pembaruan data melalui unggahan file CSV (transactions / shifts) dengan validasi skema ketat
- Visualisasi interaktif Plotly: tren harian, peta OpenStreetMap 6 titik (Tiban–Sekupang–Batam Centre),
  heatmap jam ramai (peak hours), performa 14 menu primer UMKM, & laporan rekonsiliasi shift
- Integrasi langsung model ML (Ridge Regression) untuk simulator prediksi kebutuhan stok cup harian
- Fitur unduh rekap CSV (penjualan harian & laporan rekonsiliasi)
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# KONFIGURASI HALAMAN & GAYA VISUAL KOPI SEWU
# ==============================================================================
st.set_page_config(
    page_title="Kopi Sewu Batam — Dasbor Analitik Operasional",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .hero-banner {
        background: linear-gradient(120deg, #3E2723 0%, #6F4E37 60%, #A1887F 100%);
        color: #FFFFFF;
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .hero-banner h1 {
        margin: 0 0 0.25rem 0;
        font-size: 1.65rem;
        color: #FFFFFF;
    }
    .hero-banner p {
        margin: 0;
        font-size: 0.92rem;
        opacity: 0.94;
    }
    .sim-badge {
        display: inline-block;
        background-color: rgba(255, 243, 205, 0.22);
        border: 1px solid rgba(255, 243, 205, 0.6);
        color: #FFF8E1;
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-top: 0.55rem;
    }
    div[data-testid="stMetric"] {
        background-color: #FAF7F2;
        border: 1px solid #EAE0D5;
        border-radius: 10px;
        padding: 0.75rem 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# PATH & KONSTANTA DOMAIN
# ==============================================================================
DS_DIR = Path(__file__).resolve().parents[1]
PROC_DIR = DS_DIR / "data" / "processed"
FS_DIR = DS_DIR / "data" / "handoff_fs"
MODEL_PATH = DS_DIR / "models" / "cup_demand_forecaster.joblib"
FORECAST_JSON_PATH = FS_DIR / "demand_forecast.json"

REQUIRED_TX_COLS = {
    "transaction_id", "shift_id", "transaction_timestamp", "cart_id", "location_id",
    "menu_id", "menu_name", "category", "unit_type", "qty", "unit_price",
    "total_price", "hpp_asumsi_total", "payment_method", "order_type",
}
REQUIRED_SHIFT_COLS = {
    "shift_id", "shift_date", "cart_id", "location_id", "mode_operasi",
    "start_time", "end_time", "weather", "cup_dibawa", "cup_sisa",
    "setoran_tunai_fisik", "mutasi_qris_aktual", "status",
}

ZONE_PEAK_HOURS: dict[str, set[int]] = {
    "outlet_olahraga_komunitas": {17, 18, 19, 20},
    "komersial_kuliner": {12, 16, 17, 18, 19},
    "pasar_perumahan": {8, 9, 10, 16, 17},
    "kampus": {10, 11, 12, 13, 16, 17},
    "perkantoran_ruang_publik": {9, 12, 17, 18, 19, 20},
    "kampus_perkantoran": {10, 11, 12, 13, 16, 17, 18},
}

ENG_CAT = ["cart_id", "location_id", "mode_operasi", "weather", "shift_slot", "loc_x_daytype", "armada_x_weather"]
ENG_NUM = [
    "duration_hours", "day_of_week", "is_weekend", "is_payday",
    "start_hour", "end_hour", "is_campus_weekend", "peak_hour_overlap",
    "loc_daytype_hist_rate", "cart_hist_rate", "expected_cups_hist_prior",
]


def format_idr(val: float | int) -> str:
    return f"Rp {int(round(val)):,}".replace(",", ".")


# ==============================================================================
# PEMUATAN DATA, REKONSILIASI DINAMIS, & MODEL ML
# ==============================================================================
@st.cache_data(show_spinner=False)
def load_default_datasets() -> dict[str, pd.DataFrame]:
    return {
        "menu": pd.read_csv(PROC_DIR / "menu_clean.csv"),
        "locations": pd.read_csv(PROC_DIR / "locations_clean.csv"),
        "carts": pd.read_csv(PROC_DIR / "carts_clean.csv"),
        "shifts": pd.read_csv(PROC_DIR / "shifts_clean.csv"),
        "tx": pd.read_csv(PROC_DIR / "transactions_clean.csv"),
    }


@st.cache_resource(show_spinner=False)
def load_forecast_model() -> Any | None:
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None


@st.cache_data(show_spinner=False)
def load_forecast_json() -> dict[str, Any] | None:
    if FORECAST_JSON_PATH.exists():
        return json.loads(FORECAST_JSON_PATH.read_text(encoding="utf-8"))
    return None


def compute_reconciliation(shifts_df: pd.DataFrame, tx_df: pd.DataFrame) -> pd.DataFrame:
    """Menghitung tabel rekonsiliasi shift secara dinamis (mendukung data unggahan baru)."""
    sh = shifts_df.copy()
    sh["start_dt"] = pd.to_datetime(sh["start_time"])
    sh["end_dt"] = pd.to_datetime(sh["end_time"])
    if "duration_hours" not in sh.columns:
        sh["duration_hours"] = ((sh["end_dt"] - sh["start_dt"]).dt.total_seconds() / 3600.0).round(2)
    if "cup_sisa_is_missing" not in sh.columns:
        sh["cup_sisa_is_missing"] = sh["cup_sisa"].isna()

    cup_agg = tx_df.loc[tx_df["unit_type"] == "cup"].groupby("shift_id")["qty"].sum()
    bottle_agg = tx_df.loc[tx_df["unit_type"] == "botol"].groupby("shift_id")["qty"].sum()
    tx_cnt = tx_df.groupby("shift_id")["transaction_id"].count()
    rev_agg = tx_df.groupby("shift_id")["total_price"].sum()
    hpp_agg = tx_df.groupby("shift_id")["hpp_asumsi_total"].sum()
    cash_agg = tx_df.loc[tx_df["payment_method"] == "Tunai"].groupby("shift_id")["total_price"].sum()
    qris_agg = tx_df.loc[tx_df["payment_method"] == "QRIS"].groupby("shift_id")["total_price"].sum()
    unk_agg = tx_df.loc[tx_df["payment_method"] == "Tidak Diketahui"].groupby("shift_id")["total_price"].sum()

    sh["tx_count"] = sh["shift_id"].map(tx_cnt).fillna(0).astype(int)
    sh["cup_tercatat_sistem"] = sh["shift_id"].map(cup_agg).fillna(0).astype(int)
    sh["botol_tercatat_sistem"] = sh["shift_id"].map(bottle_agg).fillna(0).astype(int)
    sh["omzet_tercatat_sistem"] = sh["shift_id"].map(rev_agg).fillna(0).astype(int)
    sh["hpp_asumsi_shift"] = sh["shift_id"].map(hpp_agg).fillna(0).astype(int)
    sh["expected_tunai_sistem"] = sh["shift_id"].map(cash_agg).fillna(0).astype(int)
    sh["expected_qris_sistem"] = sh["shift_id"].map(qris_agg).fillna(0).astype(int)
    sh["nominal_metode_tidak_diketahui"] = sh["shift_id"].map(unk_agg).fillna(0).astype(int)

    sh["cup_terpakai_fisik"] = np.where(sh["cup_sisa"].isna(), np.nan, sh["cup_dibawa"] - sh["cup_sisa"])
    sh["selisih_cup"] = np.where(sh["cup_sisa"].isna(), np.nan, sh["cup_terpakai_fisik"] - sh["cup_tercatat_sistem"])
    sh["selisih_tunai_idr"] = sh["setoran_tunai_fisik"] - sh["expected_tunai_sistem"]
    sh["selisih_qris_idr"] = sh["mutasi_qris_aktual"] - sh["expected_qris_sistem"]
    sh["rev_per_hour"] = np.where(sh["duration_hours"] > 0, sh["omzet_tercatat_sistem"] / sh["duration_hours"], 0.0)
    sh["cups_per_hour"] = np.where(sh["duration_hours"] > 0, sh["cup_tercatat_sistem"] / sh["duration_hours"], 0.0)

    def _status(row: pd.Series) -> str:
        if pd.isna(row["cup_sisa"]):
            return "data_tidak_lengkap"
        ac = abs(int(row["selisih_cup"]))
        am = abs(int(row["selisih_tunai_idr"]))
        if ac >= 3 or am > 30000:
            return "selisih_tinggi"
        if ac >= 1 or am > 5000:
            return "perlu_cek"
        return "cocok"

    sh["reconciliation_status"] = sh.apply(_status, axis=1)
    return sh


def prepare_enriched_tables(
    raw_data: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    menu = raw_data["menu"].copy()
    locations = raw_data["locations"].copy()
    carts = raw_data["carts"].copy()
    shifts = raw_data["shifts"].copy()
    tx = raw_data["tx"].copy()

    recon = compute_reconciliation(shifts, tx)

    tx["tx_dt"] = pd.to_datetime(tx["transaction_timestamp"])
    tx["tx_date"] = tx["tx_dt"].dt.date
    tx["month"] = tx["tx_dt"].dt.to_period("M").astype(str)
    tx["day_of_week"] = tx["tx_dt"].dt.day_of_week
    tx["is_weekend"] = tx["day_of_week"] >= 5
    tx["day_type"] = np.where(tx["is_weekend"], "Akhir Pekan", "Hari Kerja")
    tx["hour"] = tx["tx_dt"].dt.hour
    tx["estimated_profit"] = tx["total_price"] - tx["hpp_asumsi_total"]
    tx = tx.merge(locations[["location_id", "location_name", "area", "zone_type"]], on="location_id", how="left")
    tx = tx.merge(
        carts[["cart_id", "cart_name", "unit_type", "default_mode"]].rename(columns={"unit_type": "armada_type"}),
        on="cart_id",
        how="left",
    )
    tx = tx.merge(shifts[["shift_id", "weather", "mode_operasi"]], on="shift_id", how="left")

    recon["shift_dt"] = pd.to_datetime(recon["shift_date"])
    recon["shift_date_obj"] = recon["shift_dt"].dt.date
    recon["is_weekend"] = recon["shift_dt"].dt.day_of_week >= 5
    recon["day_type"] = np.where(recon["is_weekend"], "Akhir Pekan", "Hari Kerja")
    recon = recon.merge(locations[["location_id", "location_name", "area", "zone_type", "latitude", "longitude"]], on="location_id", how="left")
    recon = recon.merge(
        carts[["cart_id", "cart_name", "unit_type", "default_mode", "cup_capacity"]].rename(columns={"unit_type": "armada_type"}),
        on="cart_id",
        how="left",
    )
    return menu, locations, carts, recon, tx


# ==============================================================================
# SIDEBAR: PEMBARUAN DATA (UPLOAD CSV) & FILTER INTERAKTIF
# ==============================================================================
base_data = load_default_datasets()
active_source_note = "Dataset Bersih Default (Agt–Okt 2026)"

with st.sidebar:
    st.markdown("## ☕ Kopi Sewu Analytics")
    st.caption("Tim A26-CS267 (Karsa) • Divisi Data Science")

    with st.expander("📤 Pembaruan Data (Unggah CSV)", expanded=False):
        st.caption(
            "Unggah berkas `transactions_clean.csv` dan/atau `shifts_clean.csv` baru untuk memperbarui seluruh grafik secara langsung."
        )
        up_tx = st.file_uploader("Unggah Transaksi (.csv)", type=["csv"], key="upload_tx")
        up_sh = st.file_uploader("Unggah Shifts (.csv)", type=["csv"], key="upload_shifts")

        if up_tx is not None:
            try:
                new_tx = pd.read_csv(up_tx)
                missing_c = REQUIRED_TX_COLS - set(new_tx.columns)
                if missing_c:
                    st.error(f"Kolom transaksi belum lengkap: {', '.join(sorted(missing_c))}")
                else:
                    base_data["tx"] = new_tx
                    active_source_note = f"Unggahan Pengguna ({up_tx.name})"
                    st.success(f"Berhasil memuat {len(new_tx):,} baris transaksi.")
            except Exception as exc:
                st.error(f"Gagal membaca CSV transaksi: {exc}")

        if up_sh is not None:
            try:
                new_sh = pd.read_csv(up_sh)
                missing_s = REQUIRED_SHIFT_COLS - set(new_sh.columns)
                if missing_s:
                    st.error(f"Kolom shifts belum lengkap: {', '.join(sorted(missing_s))}")
                else:
                    base_data["shifts"] = new_sh
                    active_source_note = f"Unggahan Pengguna ({up_sh.name})"
                    st.success(f"Berhasil memuat {len(new_sh):,} baris shift.")
            except Exception as exc:
                st.error(f"Gagal membaca CSV shifts: {exc}")

    menu_df, loc_df, cart_df, recon_all, tx_all = prepare_enriched_tables(base_data)

    st.divider()
    st.subheader("🔎 Filter Operasional")

    min_d = min(tx_all["tx_date"].min(), recon_all["shift_date_obj"].min())
    max_d = max(tx_all["tx_date"].max(), recon_all["shift_date_obj"].max())
    date_range = st.date_input(
        "Rentang Tanggal",
        value=(min_d, max_d),
        min_value=date(2026, 1, 1),
        max_value=date(2026, 12, 31),
        key="filter_date_range",
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_d, end_d = date_range
    else:
        start_d, end_d = min_d, max_d

    all_carts = cart_df["cart_id"].tolist()
    cart_labels = dict(zip(cart_df["cart_id"], cart_df["cart_id"] + " — " + cart_df["cart_name"]))
    sel_carts = st.multiselect(
        "Unit Armada",
        options=all_carts,
        default=all_carts,
        format_func=lambda cid: cart_labels.get(cid, cid),
        key="filter_carts",
    )

    all_locs = loc_df["location_id"].tolist()
    loc_labels = dict(zip(loc_df["location_id"], loc_df["location_id"] + " — " + loc_df["location_name"]))
    sel_locs = st.multiselect(
        "Titik Lokasi",
        options=all_locs,
        default=all_locs,
        format_func=lambda lid: loc_labels.get(lid, lid),
        key="filter_locs",
    )

    weather_opts = ["Cerah", "Berawan", "Hujan"]
    sel_weather = st.multiselect("Kondisi Cuaca", options=weather_opts, default=weather_opts, key="filter_weather")

    day_filter = st.radio(
        "Tipe Hari",
        options=["Semua Hari", "Hari Kerja (Sen–Jum)", "Akhir Pekan (Sab–Min)"],
        index=0,
        key="filter_day_type",
    )

    cat_opts = ["Kopi", "Non Kopi", "Botolan"]
    sel_cats = st.multiselect("Kategori Menu", options=cat_opts, default=cat_opts, key="filter_cats")

    st.divider()
    st.caption(f"Sumber aktif: **{active_source_note}**")

# Terapkan filter ke transaksi & rekonsiliasi shift
tx_f = tx_all[
    (tx_all["tx_date"] >= start_d)
    & (tx_all["tx_date"] <= end_d)
    & (tx_all["cart_id"].isin(sel_carts))
    & (tx_all["location_id"].isin(sel_locs))
    & (tx_all["weather"].isin(sel_weather))
    & (tx_all["category"].isin(sel_cats))
].copy()

recon_f = recon_all[
    (recon_all["shift_date_obj"] >= start_d)
    & (recon_all["shift_date_obj"] <= end_d)
    & (recon_all["cart_id"].isin(sel_carts))
    & (recon_all["location_id"].isin(sel_locs))
    & (recon_all["weather"].isin(sel_weather))
].copy()

if day_filter == "Hari Kerja (Sen–Jum)":
    tx_f = tx_f[~tx_f["is_weekend"]]
    recon_f = recon_f[~recon_f["is_weekend"]]
elif day_filter == "Akhir Pekan (Sab–Min)":
    tx_f = tx_f[tx_f["is_weekend"]]
    recon_f = recon_f[recon_f["is_weekend"]]

# ==============================================================================
# HERO BANNER & TRANSPARENCY NOTICE
# ==============================================================================
st.markdown(
    f"""
    <div class="hero-banner">
        <h1>☕ Dasbor Pemantauan Operasional & Prediksi Stok — Kopi Sewu Batam</h1>
        <p>Koridor Tiban • Sekupang • Batam Centre &nbsp;|&nbsp; Periode Filter: <b>{start_d.strftime('%d %b %Y')} – {end_d.strftime('%d %b %Y')}</b></p>
        <span class="sim-badge">DATA SIMULASI CAPSTONE (Agt–Okt 2026) • Katalog 14 Menu &amp; Koordinat Outlet Primer UMKM</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# TABS UTAMA (5 TAB)
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Ringkasan & Tren",
    "🗺️ Peta, Armada & Jam Ramai",
    "🥤 Performa 14 Menu",
    "🧾 Rekonsiliasi & QRIS",
    "🤖 Prediksi Stok Cup (ML)",
])

# ------------------------------------------------------------------------------
# TAB 1: RINGKASAN EKSEKUTIF & TREN PENJUALAN (BQ-01)
# ------------------------------------------------------------------------------
with tab1:
    if tx_f.empty:
        st.info("Data belum tersedia untuk kombinasi filter tanggal/armada/lokasi yang dipilih. Silakan perluas filter di sidebar.")
    else:
        tot_rev = int(tx_f["total_price"].sum())
        tot_prof = int(tx_f["estimated_profit"].sum())
        margin_pct = (tot_prof / tot_rev * 100) if tot_rev > 0 else 0.0
        tot_cups = int(tx_f.loc[tx_f["unit_type"] == "cup", "qty"].sum())
        tot_bottles = int(tx_f.loc[tx_f["unit_type"] == "botol", "qty"].sum())
        aov = int(round(tot_rev / len(tx_f)))
        known_pay = tx_f[tx_f["payment_method"] != "Tidak Diketahui"]
        qris_pct = float((known_pay["payment_method"] == "QRIS").mean() * 100) if len(known_pay) else 0.0

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Total Omzet", format_idr(tot_rev))
        c2.metric("Est. Margin Kotor*", format_idr(tot_prof), f"{margin_pct:.1f}%")
        c3.metric("Total Cup Terjual", f"{tot_cups:,}".replace(",", "."))
        c4.metric("Total Botolan", f"{tot_bottles:,}".replace(",", "."))
        c5.metric("Total Transaksi", f"{len(tx_f):,}".replace(",", "."), f"AOV {format_idr(aov)}")
        c6.metric("Adopsi QRIS", f"{qris_pct:.1f}%", f"Tunai {100 - qris_pct:.1f}%")
        st.caption("*Estimasi margin kotor dihitung menggunakan asumsi HPP sintetis (~46% rata-rata tertimbang) untuk simulasi prototipe.")

        # Agregasi harian
        daily = (
            tx_f.groupby("tx_date", sort=True)
            .agg(
                revenue=("total_price", "sum"),
                profit=("estimated_profit", "sum"),
                transactions=("transaction_id", "count"),
                cups=("qty", lambda s: s[tx_f.loc[s.index, "unit_type"] == "cup"].sum()),
                bottles=("qty", lambda s: s[tx_f.loc[s.index, "unit_type"] == "botol"].sum()),
            )
            .reset_index()
        )
        daily["ma7"] = daily["revenue"].rolling(7, min_periods=1).mean()
        w_map = recon_f.groupby("shift_date_obj")["weather"].agg(lambda s: s.mode().iloc[0]).to_dict() if not recon_f.empty else {}
        daily["weather"] = daily["tx_date"].map(w_map).fillna("Cerah")

        col_l, col_r = st.columns([1.6, 1])
        with col_l:
            fig_trend = go.Figure()
            fig_trend.add_trace(
                go.Scatter(
                    x=daily["tx_date"], y=daily["revenue"], mode="lines",
                    name="Omzet Harian", line=dict(color="#90CDF4", width=1.6),
                    hovertemplate="Tanggal: %{x}<br>Omzet: Rp %{y:,.0f}<extra></extra>",
                )
            )
            fig_trend.add_trace(
                go.Scatter(
                    x=daily["tx_date"], y=daily["ma7"], mode="lines",
                    name="Moving Average 7 Hari", line=dict(color="#3E2723", width=2.8),
                    hovertemplate="Tanggal: %{x}<br>MA7: Rp %{y:,.0f}<extra></extra>",
                )
            )
            rain_d = daily[daily["weather"] == "Hujan"]
            if not rain_d.empty:
                fig_trend.add_trace(
                    go.Scatter(
                        x=rain_d["tx_date"], y=rain_d["revenue"], mode="markers",
                        name="Hari Hujan", marker=dict(color="#E53E3E", size=7),
                        hovertemplate="Hari Hujan (%{x})<br>Omzet: Rp %{y:,.0f}<extra></extra>",
                    )
                )
            fig_trend.update_layout(
                title="Tren Omzet Harian & Moving Average 7 Hari",
                xaxis_title="Tanggal", yaxis_title="Omzet (Rp)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=390, margin=dict(l=20, r=20, t=55, b=20),
            )
            st.plotly_chart(fig_trend, width="stretch")

        with col_r:
            if not recon_f.empty:
                w_df = (
                    recon_f.groupby(["weather", "armada_type"])["rev_per_hour"]
                    .mean()
                    .reset_index()
                )
                w_df["Armada"] = w_df["armada_type"].map({"outlet_tetap": "Outlet Tetap", "gerobak_keliling": "Gerobak Keliling"})
                fig_w = px.bar(
                    w_df, x="weather", y="rev_per_hour", color="Armada", barmode="group",
                    category_orders={"weather": ["Cerah", "Berawan", "Hujan"]},
                    color_discrete_map={"Outlet Tetap": "#6F4E37", "Gerobak Keliling": "#DD6B20"},
                    title="Dampak Cuaca: Omzet/Jam Outlet vs Gerobak",
                    labels={"weather": "Cuaca", "rev_per_hour": "Omzet / Jam (Rp)"},
                    height=390,
                )
                fig_w.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    margin=dict(l=20, r=20, t=55, b=20),
                )
                st.plotly_chart(fig_w, width="stretch")

        # Ekspor Rekap Penjualan Harian (CSV)
        csv_daily = daily.rename(columns={
            "tx_date": "tanggal", "revenue": "omzet_idr", "profit": "estimasi_margin_idr",
            "transactions": "jumlah_transaksi", "cups": "cup_terjual", "bottles": "botol_terjual",
        }).drop(columns=["ma7"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Unduh Rekap Penjualan Harian (CSV)",
            data=csv_daily,
            file_name=f"rekap_penjualan_kopi_sewu_{start_d}_{end_d}.csv",
            mime="text/csv",
        )

# ------------------------------------------------------------------------------
# TAB 2: PETA LOKASI, PRODUKTIVITAS ARMADA, & JAM RAMAI (BQ-02, BQ-03, BQ-04)
# ------------------------------------------------------------------------------
with tab2:
    if recon_f.empty or tx_f.empty:
        st.info("Data shift belum tersedia untuk kombinasi filter saat ini.")
    else:
        loc_agg = (
            recon_f.groupby(["location_id", "location_name", "area", "zone_type", "latitude", "longitude"])
            .agg(
                total_shifts=("shift_id", "count"),
                total_hours=("duration_hours", "sum"),
                total_revenue=("omzet_tercatat_sistem", "sum"),
                total_cups=("cup_tercatat_sistem", "sum"),
            )
            .reset_index()
        )
        loc_agg["rev_per_hour"] = (loc_agg["total_revenue"] / loc_agg["total_hours"]).round(0).astype(int)
        loc_agg["cups_per_hour"] = (loc_agg["total_cups"] / loc_agg["total_hours"]).round(2)
        loc_agg = loc_agg.sort_values("rev_per_hour", ascending=False)

        col_map, col_wdwe = st.columns([1.2, 1])
        with col_map:
            st.subheader("🗺️ Peta Sebaran & Produktivitas 6 Titik (Tiban – Sekupang – Batam Centre)")
            map_fn = px.scatter_map if hasattr(px, "scatter_map") else px.scatter_mapbox
            map_kwargs: dict[str, Any] = dict(
                data_frame=loc_agg,
                lat="latitude",
                lon="longitude",
                size="rev_per_hour",
                color="rev_per_hour",
                color_continuous_scale="YlOrBr",
                hover_name="location_name",
                hover_data={
                    "location_id": True, "area": True, "total_shifts": True,
                    "rev_per_hour": ":,.0f", "cups_per_hour": ":.2f",
                    "latitude": False, "longitude": False,
                },
                zoom=11.3,
                center={"lat": 1.118, "lon": 104.005},
                size_max=28,
                height=420,
            )
            if hasattr(px, "scatter_map"):
                map_kwargs["map_style"] = "open-street-map"
            else:
                map_kwargs["mapbox_style"] = "open-street-map"
            fig_map = map_fn(**map_kwargs)
            fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0), coloraxis_colorbar_title="Rp/Jam")
            st.plotly_chart(fig_map, width="stretch")

        with col_wdwe:
            st.subheader("📊 Kontras Omzet/Jam: Hari Kerja vs Akhir Pekan")
            wdwe = (
                recon_f.groupby(["location_name", "day_type"])
                .apply(
                    lambda g: g["omzet_tercatat_sistem"].sum() / g["duration_hours"].sum(),
                    include_groups=False,
                )
                .rename("rev_per_hour")
                .reset_index()
            )
            fig_wdwe = px.bar(
                wdwe, y="location_name", x="rev_per_hour", color="day_type", barmode="group",
                orientation="h",
                color_discrete_map={"Hari Kerja": "#2B6CB0", "Akhir Pekan": "#ED8936"},
                labels={"location_name": "", "rev_per_hour": "Omzet / Jam (Rp)", "day_type": "Tipe Hari"},
                height=420,
            )
            fig_wdwe.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=10, r=15, t=35, b=10),
            )
            st.plotly_chart(fig_wdwe, width="stretch")

        st.divider()
        st.subheader("🔥 Peta Jam Puncak Keramaian (Peak Hours — Rata-rata Cup per Jam Aktif)")
        hm_mode = st.radio(
            "Tampilkan Heatmap untuk:",
            options=["Hari Kerja", "Akhir Pekan"],
            horizontal=True,
            key="hm_day_toggle",
        )
        recon_hm = recon_f[recon_f["day_type"] == hm_mode]
        tx_hm = tx_f[(tx_f["day_type"] == hm_mode) & (tx_f["unit_type"] == "cup")]
        if recon_hm.empty:
            st.info(f"Tidak ada data shift pada tipe hari **{hm_mode}** untuk filter aktif.")
        else:
            exp_rows = []
            for _, r in recon_hm.iterrows():
                s_h = pd.to_datetime(r["start_time"]).hour
                e_dt = pd.to_datetime(r["end_time"])
                e_h = e_dt.hour if e_dt.minute >= 30 else e_dt.hour - 1
                for hr in range(s_h, e_h + 1):
                    exp_rows.append({"location_name": r["location_name"], "hour": hr})
            act_df = pd.DataFrame(exp_rows).groupby(["location_name", "hour"]).size().rename("active_hrs").reset_index()
            cup_hr = tx_hm.groupby(["location_name", "hour"])["qty"].sum().rename("cups").reset_index()
            hm_m = act_df.merge(cup_hr, on=["location_name", "hour"], how="left").fillna({"cups": 0})
            hm_m["avg_cups"] = (hm_m["cups"] / hm_m["active_hrs"]).round(1)
            piv = hm_m.pivot(index="location_name", columns="hour", values="avg_cups").reindex(columns=list(range(7, 22)))
            piv.columns = [f"{h:02d}:00" for h in range(7, 22)]
            fig_hm = px.imshow(
                piv, text_auto=".1f", color_continuous_scale="YlOrRd", aspect="auto",
                labels=dict(x="Jam Operasional (WIB)", y="", color="Cup / Jam"),
                height=340,
            )
            fig_hm.update_layout(margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig_hm, width="stretch")

        st.divider()
        st.subheader("🚚 Performa 5 Unit Armada & Deteksi Shift Blind Spot (< Rp 50.000/jam)")
        cart_agg = (
            recon_f.groupby(["cart_id", "cart_name", "default_mode"])
            .agg(
                shift=("shift_id", "count"),
                jam_aktif=("duration_hours", "sum"),
                total_omzet=("omzet_tercatat_sistem", "sum"),
                total_cup=("cup_tercatat_sistem", "sum"),
                shift_blind_spot=("rev_per_hour", lambda s: int((s < 50000).sum())),
            )
            .reset_index()
        )
        cart_agg["omzet_per_jam"] = (cart_agg["total_omzet"] / cart_agg["jam_aktif"]).round(0).astype(int)
        st.dataframe(cart_agg, width="stretch", hide_index=True)

# ------------------------------------------------------------------------------
# TAB 3: PERFORMA 14 MENU PRIMER & PREFERENSI ZONA (BQ-05)
# ------------------------------------------------------------------------------
with tab3:
    if tx_f.empty:
        st.info("Data menu belum tersedia untuk filter aktif.")
    else:
        sort_metric = st.radio(
            "Urutkan 14 Menu berdasarkan:",
            options=["Total Omzet (Rp)", "Kuantitas Terjual", "Estimasi Margin Kotor (Rp)"],
            horizontal=True,
            key="menu_sort_metric",
        )
        sort_col = {
            "Total Omzet (Rp)": "total_revenue",
            "Kuantitas Terjual": "qty_sold",
            "Estimasi Margin Kotor (Rp)": "total_profit",
        }[sort_metric]

        m_perf = (
            tx_f.groupby(["menu_id", "menu_name", "category", "unit_type", "unit_price"])
            .agg(
                transactions=("transaction_id", "count"),
                qty_sold=("qty", "sum"),
                total_revenue=("total_price", "sum"),
                total_profit=("estimated_profit", "sum"),
            )
            .reset_index()
            .sort_values(sort_col, ascending=False)
        )
        m_perf["margin_pct"] = (m_perf["total_profit"] / m_perf["total_revenue"] * 100).round(1)

        col_m1, col_m2 = st.columns([1.3, 1])
        with col_m1:
            fig_menu = px.bar(
                m_perf, y="menu_name", x=sort_col, color="category", orientation="h",
                color_discrete_map={"Kopi": "#2B6CB0", "Non Kopi": "#D53F8C", "Botolan": "#D69E2E"},
                title=f"Ranking 14 Menu Asli Kopi Sewu — {sort_metric}",
                labels={"menu_name": "", sort_col: sort_metric, "category": "Kategori"},
                hover_data={"unit_price": ":,.0f", "qty_sold": ":,", "margin_pct": ":.1f"},
                height=500,
            )
            fig_menu.update_yaxes(autorange="reversed")
            fig_menu.update_layout(margin=dict(l=10, r=20, t=45, b=15))
            st.plotly_chart(fig_menu, width="stretch")

        with col_m2:
            loc_cat = tx_f.groupby(["location_name", "category"])["total_price"].sum().reset_index()
            loc_tot = loc_cat.groupby("location_name")["total_price"].transform("sum")
            loc_cat["share_pct"] = (loc_cat["total_price"] / loc_tot * 100).round(1)
            fig_cat = px.bar(
                loc_cat, y="location_name", x="share_pct", color="category", orientation="h",
                color_discrete_map={"Kopi": "#2B6CB0", "Non Kopi": "#D53F8C", "Botolan": "#D69E2E"},
                title="Komposisi Kategori Omzet (%) per Lokasi",
                labels={"location_name": "", "share_pct": "Proporsi Omzet (%)", "category": "Kategori"},
                text="share_pct",
                height=500,
            )
            fig_cat.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
            fig_cat.update_layout(barmode="stack", xaxis_range=[0, 100], margin=dict(l=10, r=15, t=45, b=15))
            st.plotly_chart(fig_cat, width="stretch")

        bulk_sub = tx_f[tx_f["order_type"] == "bulk_order"]
        st.info(
            f"**Kontribusi Valid Bulk Order pada Filter Aktif:** {len(bulk_sub)} transaksi "
            f"({len(bulk_sub)/len(tx_f)*100:.2f}% struk) menyumbang **{format_idr(bulk_sub['total_price'].sum())}** "
            f"({bulk_sub['total_price'].sum()/tx_f['total_price'].sum()*100:.2f}% total omzet)."
        )

# ------------------------------------------------------------------------------
# TAB 4: REKONSILIASI SETORAN & PEMBAYARAN (BQ-06)
# ------------------------------------------------------------------------------
with tab4:
    if recon_f.empty:
        st.info("Data rekonsiliasi shift belum tersedia untuk filter aktif.")
    else:
        st_vc = recon_f["reconciliation_status"].value_counts().to_dict()
        valid_cup_sub = recon_f[~recon_f["cup_sisa_is_missing"]]
        tot_cup_diff = int(valid_cup_sub["selisih_cup"].sum()) if not valid_cup_sub.empty else 0
        tot_abs_cash = int(recon_f["selisih_tunai_idr"].abs().sum())

        r1, r2, r3, r4, r5 = st.columns(5)
        r1.metric("Shift Cocok", f"{st_vc.get('cocok', 0)}")
        r2.metric("Perlu Cek", f"{st_vc.get('perlu_cek', 0)}")
        r3.metric("Selisih Tinggi", f"{st_vc.get('selisih_tinggi', 0)}")
        r4.metric("Cup Sisa Kosong", f"{st_vc.get('data_tidak_lengkap', 0)}")
        r5.metric("Total Selisih Cup", f"{tot_cup_diff} cup", f"Kas Abs {format_idr(tot_abs_cash)}")

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            rc_cart = recon_f.groupby(["cart_id", "reconciliation_status"]).size().reset_index(name="shifts")
            fig_rc = px.bar(
                rc_cart, x="cart_id", y="shifts", color="reconciliation_status", barmode="stack",
                color_discrete_map={
                    "cocok": "#38A169", "perlu_cek": "#ECC94B",
                    "selisih_tinggi": "#E53E3E", "data_tidak_lengkap": "#A0AEC0",
                },
                title="Distribusi Status Rekonsiliasi per Armada",
                labels={"cart_id": "Unit", "shifts": "Jumlah Shift", "reconciliation_status": "Status"},
                height=360,
            )
            st.plotly_chart(fig_rc, width="stretch")

        with col_r2:
            known_f = tx_f[tx_f["payment_method"] != "Tidak Diketahui"]
            if not known_f.empty:
                pl = known_f.groupby(["location_name", "payment_method"]).size().reset_index(name="cnt")
                pl["pct"] = (pl["cnt"] / pl.groupby("location_name")["cnt"].transform("sum") * 100).round(1)
                fig_pl = px.bar(
                    pl, y="location_name", x="pct", color="payment_method", orientation="h",
                    color_discrete_map={"QRIS": "#319795", "Tunai": "#ED8936"},
                    title="Proporsi Pembayaran QRIS vs Tunai per Lokasi",
                    labels={"location_name": "", "pct": "Proporsi (%)", "payment_method": "Metode"},
                    text="pct", height=360,
                )
                fig_pl.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
                fig_pl.update_layout(barmode="stack", xaxis_range=[0, 100])
                st.plotly_chart(fig_pl, width="stretch")

        sel_status = st.multiselect(
            "Filter Status Rekonsiliasi pada Tabel Detail:",
            options=["cocok", "perlu_cek", "selisih_tinggi", "data_tidak_lengkap"],
            default=["selisih_tinggi", "perlu_cek", "data_tidak_lengkap"],
            key="filter_recon_status",
        )
        detail_cols = [
            "shift_date", "shift_id", "cart_id", "location_name", "weather",
            "cup_dibawa", "cup_sisa", "cup_tercatat_sistem", "selisih_cup",
            "setoran_tunai_fisik", "expected_tunai_sistem", "selisih_tunai_idr",
            "reconciliation_status",
        ]
        detail_df = recon_f[recon_f["reconciliation_status"].isin(sel_status)][detail_cols].sort_values(
            ["shift_date", "shift_id"], ascending=[False, False]
        )
        st.dataframe(detail_df, width="stretch", hide_index=True)

        st.download_button(
            label="⬇️ Unduh Laporan Rekonsiliasi Shift (CSV)",
            data=detail_df.to_csv(index=False).encode("utf-8"),
            file_name=f"rekonsiliasi_kopi_sewu_{start_d}_{end_d}.csv",
            mime="text/csv",
        )

# ------------------------------------------------------------------------------
# TAB 5: SIMULATOR PREDIKSI STOK CUP BERBASIS ML (BQ-07 — SIDE QUEST DS #3)
# ------------------------------------------------------------------------------
with tab5:
    st.subheader("🤖 Simulator Prediksi Kebutuhan Cup per Shift (Model Ridge Regression)")
    model_pipe = load_forecast_model()
    fc_json = load_forecast_json()

    if model_pipe is None or fc_json is None:
        st.warning("Artefak model `models/cup_demand_forecaster.joblib` atau `demand_forecast.json` belum ditemukan.")
    else:
        ev = fc_json["evaluation_summary"]
        safety_buf = int(fc_json["meta"]["safety_buffer_cups"])

        # Hitung laju historis terbaru dari data aktif untuk fitur input model
        latest_loc_rate = (
            recon_all.groupby(["location_id", "is_weekend"])["cups_per_hour"]
            .apply(lambda s: float(s.tail(7).mean()))
            .to_dict()
        )
        latest_cart_rate = (
            recon_all.groupby("cart_id")["cups_per_hour"]
            .apply(lambda s: float(s.tail(7).mean()))
            .to_dict()
        )
        global_rate = float(recon_all["cups_per_hour"].mean())
        loc_info = loc_df.set_index("location_id").to_dict("index")
        cart_info = cart_df.set_index("cart_id").to_dict("index")

        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        sim_cart = sc1.selectbox(
            "Unit Armada", options=cart_df["cart_id"].tolist(),
            format_func=lambda cid: f"{cid} ({cart_info[cid]['cart_name']})",
            index=4, key="sim_cart",
        )
        sim_loc = sc2.selectbox(
            "Titik Lokasi", options=loc_df["location_id"].tolist(),
            format_func=lambda lid: f"{lid} — {loc_info[lid]['location_name'][:24]}",
            index=4, key="sim_loc",
        )
        sim_date = sc3.date_input("Tanggal Operasi", value=date(2026, 11, 7), key="sim_date")
        sim_weather = sc4.selectbox("Prakiraan Cuaca", options=["Cerah", "Berawan", "Hujan"], index=0, key="sim_weather")
        sim_hours = sc5.slider("Jam Buka – Tutup (WIB)", min_value=7, max_value=22, value=(15, 21), key="sim_hours")

        s_h, e_h = sim_hours
        dur = max(1.0, float(e_h - s_h))
        is_we = int(sim_date.weekday() >= 5)
        day_type = "weekend" if is_we else "weekday"
        armada_type = str(cart_info[sim_cart]["unit_type"])
        mode_op = str(cart_info[sim_cart]["default_mode"])
        zone_type = str(loc_info[sim_loc]["zone_type"])
        loc_rate = latest_loc_rate.get((sim_loc, bool(is_we)), global_rate)
        cart_rate = latest_cart_rate.get(sim_cart, global_rate)
        peaks = ZONE_PEAK_HOURS.get(zone_type, set())
        peak_ov = int(sum(1 for hr in range(s_h, e_h) if hr in peaks))

        x_row = pd.DataFrame([{
            "cart_id": sim_cart,
            "location_id": sim_loc,
            "mode_operasi": mode_op,
            "weather": sim_weather,
            "shift_slot": "full_day" if dur >= 9.0 else ("pagi" if s_h < 13 else "sore"),
            "loc_x_daytype": f"{sim_loc}_{day_type}",
            "armada_x_weather": f"{armada_type}_{sim_weather}",
            "duration_hours": dur,
            "day_of_week": int(sim_date.weekday()),
            "is_weekend": is_we,
            "is_payday": int(sim_date.day >= 25 or sim_date.day <= 3),
            "start_hour": int(s_h),
            "end_hour": int(e_h),
            "is_campus_weekend": int(sim_loc in ("LOC-04", "LOC-06") and is_we == 1),
            "peak_hour_overlap": peak_ov,
            "loc_daytype_hist_rate": float(loc_rate),
            "cart_hist_rate": float(cart_rate),
            "expected_cups_hist_prior": float(loc_rate * dur),
        }])
        pred_cups = max(1, int(round(float(model_pipe.predict(x_row[ENG_CAT + ENG_NUM])[0]))))
        rec_stock = pred_cups + safety_buf
        cap = int(cart_info[sim_cart]["cup_capacity"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Prediksi Terjual", f"{pred_cups} cup", f"Durasi {dur:.0f} jam")
        m2.metric("Rekomendasi Stok Aman", f"{rec_stock} cup", f"Termasuk buffer +{safety_buf} cup")
        m3.metric("Kapasitas Gerobak", f"{cap} cup", "Perlu restock!" if rec_stock > cap else "Cukup 1 muatan")
        m4.metric("Akurasi Model (Test)", f"MAE {ev['test_mae_cups']} cup", f"R² {ev['test_r2']} | Aman {ev['stock_coverage_test_nonbulk_pct']}%")

        if sim_loc in ("LOC-04", "LOC-06") and is_we == 1:
            st.warning(
                "⚠️ **Peringatan Blind Spot:** Titik kampus (`LOC-04` UIB / `LOC-06` Polibatam) mengalami penurunan omzet -74% s.d. -80% pada akhir pekan. "
                "Pertimbangkan relokasi ke **LOC-05 Alun-Alun Engku Putri** atau **LOC-02 Tiban Centre**!"
            )
        if rec_stock > cap:
            st.info(
                f"ℹ️ Rekomendasi stok ({rec_stock} cup) melebihi kapasitas bawaan standar `{sim_cart}` ({cap} cup). "
                "Jadwalkan pengisian ulang (restock) di pertengahan shift."
            )

        st.divider()
        st.subheader("📅 Proyeksi Kebutuhan Cup 7 Hari ke Depan (1–7 Nov 2026 — Rute Rekomendasi)")
        f7_df = pd.DataFrame([
            {
                "Tanggal": d["date"],
                "Hari": d["day_name"],
                "Periode Gajian": "Ya" if d["is_payday"] else "Tidak",
                "Prediksi (Cerah)": d["total_predicted_cups_cerah"],
                "Stok Aman (Cerah)": d["total_recommended_stock_cerah"],
                "Prediksi (Hujan)": d["total_predicted_cups_hujan"],
                "Stok Aman (Hujan)": d["total_recommended_stock_hujan"],
            }
            for d in fc_json["forecast_next_7_days"]
        ])
        fig_f7 = go.Figure()
        fig_f7.add_trace(go.Bar(x=f7_df["Hari"] + "<br>" + f7_df["Tanggal"], y=f7_df["Prediksi (Cerah)"], name="Prediksi Cup (Cerah)", marker_color="#DD6B20"))
        fig_f7.add_trace(go.Bar(x=f7_df["Hari"] + "<br>" + f7_df["Tanggal"], y=f7_df["Prediksi (Hujan)"], name="Prediksi Cup (Hujan)", marker_color="#3182CE"))
        fig_f7.update_layout(barmode="group", yaxis_title="Total Cup / Hari (5 Unit)", height=340, margin=dict(l=15, r=15, t=25, b=15))
        st.plotly_chart(fig_f7, width="stretch")
        st.dataframe(f7_df, width="stretch", hide_index=True)

        with st.expander("ℹ️ Transparansi Keterbatasan Model Prediktif"):
            for lim in fc_json["model_limitations"]:
                st.write(f"- {lim}")
