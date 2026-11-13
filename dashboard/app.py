"""Jogja Mobility dashboard (Output 2): explore the applied analyses from notebooks 03-06.

Run from the repo root:  streamlit run dashboard/app.py
Reads data/processed/ (run the pipeline first, see README) and the shared rules in src/applied.py,
so every number matches the notebooks.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from config import (CALENDAR_CSV, CITY_KAB_CODE, GOOGLE_CATEGORIES, KAB_ORDER, PROCESSED,  # noqa: E402
                    RAW_EXT)
from applied import (city_visits, kapanewon_profiles, pooled_profile, ramadan_windows,  # noqa: E402
                     ranked_origins, shifts, ramadan_analysis, RAMADAN_FOCUS_CODES, RAMADAN_MAIN_CATEGORIES)

JP_COL, G_COL, GREY = "#0F766E", "#C2410C", "#9CA3AF"
MONTHS = {"2021-12": "Des 2021", "2022-01": "Jan 2022", "2022-02": "Feb 2022"}

st.set_page_config(page_title="Jogja Mobility", layout="wide")


@st.cache_data
def load():
    daily = pd.read_parquet(PROCESSED / "daily_diy.parquet").set_index("date")
    hourly = pd.read_parquet(PROCESSED / "hourly_kapanewon.parquet",
                             columns=["kab_kota", "kapanewon_code", "kapanewon", "date", "hour", "n_maids",
                                      "share_of_own_day", "is_day_off", "is_holiday"])
    hourly["date"] = hourly["date"].astype("datetime64[ns]")
    od = pd.read_parquet(PROCESSED / "od_dec_feb.parquet")
    od["month"] = od.month.astype(str)
    cal = pd.read_csv(CALENDAR_CSV, parse_dates=["date"])
    g = pd.read_csv(RAW_EXT / "google_mobility" / "google_mobility_diy.csv", parse_dates=["date"]).set_index("date")
    g = g[[c for c in g.columns if c.endswith("_percent_change_from_baseline")]]
    g.columns = [next(k for k in GOOGLE_CATEGORIES if c.startswith(k)) for c in g.columns]
    return daily, hourly, od, cal, g


@st.cache_data
def kap_names(hourly):
    n = hourly.drop_duplicates("kapanewon_code").set_index("kapanewon_code")[["kab_kota", "kapanewon"]]
    n["label"] = n.kapanewon.str.title() + " (" + n.kab_kota.str.title() + ")"
    return n.sort_values(["kab_kota", "kapanewon"])


@st.cache_data
def profiles_by_dayoff(hourly):
    return kapanewon_profiles(hourly, by=["is_day_off"])


@st.cache_data
def kab_profiles(hourly):
    return pooled_profile(hourly, group="kab_kota")


@st.cache_data
def kap_holiday_shift(hourly, daily):
    dev = hourly.groupby(["date", "kapanewon_code"]).n_maids.sum().unstack(fill_value=0)
    share = dev.div(dev.sum(axis=1), axis=0)
    return shifts(share, daily, relative=True)   # log(holiday share / baseline share)


def hour_chart(lines: dict, colors: dict, dashes: dict | None = None, title=""):
    fig = go.Figure()
    for name, s in lines.items():
        fig.add_trace(go.Scatter(x=list(range(24)), y=s.values, name=name, mode="lines",
                                 line=dict(color=colors.get(name), dash=(dashes or {}).get(name, "solid"))))
    fig.update_layout(title=title, xaxis_title="Jam (WIB)", yaxis_title="Porsi device-jam dalam sehari (%)",
                      xaxis=dict(dtick=3), height=430, margin=dict(t=50, b=40), legend=dict(orientation="h", y=-0.2))
    return fig


daily, hourly, od, cal, google = load()
names = kap_names(hourly)

st.title("Mobilitas Penduduk DIY, Des 2021 - Apr 2022")
st.caption("Data: JogjaPulse (device ponsel teragregasi, Zenodo 10.5281/zenodo.23157460, CC BY 4.0) dan "
           "Google Community Mobility Reports. Device bukan orang; panel device menyusut dan bergeser ke Kota, "
           "jadi semua angka di sini berupa porsi, bukan jumlah.")

tab_rhythm, tab_ramadan, tab_visits, tab_holiday, tab_valid = st.tabs(
    ["Ritme harian", "Ramadan", "Kunjungan siang ke Kota", "Hari libur", "Seberapa bisa dipercaya?"])

# ---------------------------------------------------------------- Ritme harian (notebook 03)
with tab_rhythm:
    st.subheader("Jam berapa sebuah wilayah ramai?")
    st.write("Porsi device-jam per jam dari total sehari. Hari libur = Sabtu, Minggu, dan tanggal merah.")
    level = st.radio("Tingkat", ["Kabupaten", "Kapanewon"], horizontal=True)
    if level == "Kabupaten":
        kp = kab_profiles(hourly)
        dayoff = daily.is_day_off
        picks = st.multiselect("Kabupaten", KAB_ORDER, default=["YOGYAKARTA", "GUNUNGKIDUL"],
                               format_func=str.title)
        lines, colors, dashes = {}, {}, {}
        palette = dict(zip(KAB_ORDER, px.colors.qualitative.Set2))
        for k in picks:
            sub = kp.xs(k, level="kab_kota")
            for off, lab in [(False, "hari kerja"), (True, "hari libur")]:
                name = f"{k.title()}, {lab}"
                lines[name] = sub[dayoff.reindex(sub.index).to_numpy() == off].mean()
                colors[name], dashes[name] = palette[k], ("dash" if off else "solid")
        st.plotly_chart(hour_chart(lines, colors, dashes), use_container_width=True)
    else:
        prof = profiles_by_dayoff(hourly)
        avail = prof.index.get_level_values(0).unique()
        st.caption(f"Hanya hari dengan 24 jam lengkap (jam dengan < 5 device disensor). "
                   f"{len(avail)} dari {len(names)} kapanewon cukup datanya.")
        picks = st.multiselect("Kapanewon", list(avail), default=[c for c in ["34.71.03", "34.03.01"] if c in avail],
                               format_func=lambda c: names.label[c])
        lines, colors, dashes = {}, {}, {}
        palette = px.colors.qualitative.Set2
        for i, c in enumerate(picks):
            for off, lab in [(False, "hari kerja"), (True, "hari libur")]:
                if (c, off) in prof.index:
                    name = f"{names.kapanewon[c].title()}, {lab}"
                    lines[name] = prof.loc[(c, off)]
                    colors[name], dashes[name] = palette[i % len(palette)], ("dash" if off else "solid")
        st.plotly_chart(hour_chart(lines, colors, dashes), use_container_width=True)
    st.info("Temuan notebook 03: profil antar-kapanewon sangat mirip. Pada hari libur porsi siang turun dan "
            "porsi malam naik, paling besar di Kota Yogyakarta.")

# ---------------------------------------------------------------- Ramadan (notebook 06)
with tab_ramadan:
    st.subheader("Ramadan: jam kehadiran dan kategori tempat")
    start = cal.loc[cal.name.str.contains("government"), "date"].iloc[0]
    result = ramadan_analysis(hourly, daily, start)
    focal = result["summary"].set_index("kapanewon_code").loc[list(RAMADAN_FOCUS_CODES)].reset_index()
    st.write("12 Maret–1 April dibanding 3–23 April 2022, masing-masing 21 hari. "
             "Banguntapan dan Depok dipilih dari cerita kunjungan siang; data di sini mencakup semua "
             "perangkat yang hadir, bukan hanya perangkat berumah di sana. Hari libur tetap masuk.")
    left, right = st.columns(2)
    with left:
        plot = focal.melt(id_vars="kapanewon", value_vars=["before", "during"], var_name="Periode", value_name="Porsi (%)")
        plot["Periode"] = plot.Periode.map({"before":"Sebelum", "during":"Selama"})
        fig = px.bar(plot, x="kapanewon", y="Porsi (%)", color="Periode", barmode="group",
                     color_discrete_map={"Sebelum":GREY,"Selama":JP_COL},
                     labels={"kapanewon":"Wilayah"}, title="JogjaPulse: porsi catatan pukul 03.00–04.59")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Rata-rata porsi harian, hanya wilayah dengan 24 jam lengkap pada seluruh 42 hari. "
                   "Bukan jumlah orang atau perjalanan.")
    with right:
        gt = result["google"].set_index("category").loc[list(RAMADAN_MAIN_CATEGORIES)].reset_index()
        gt["Kategori"] = gt.category.map({"parks":"Taman", "retail_and_recreation":"Retail/rekreasi", "residential":"Waktu di rumah"})
        fig = px.bar(gt, y="Kategori", x="change_pp", orientation="h", color_discrete_sequence=[G_COL],
                     labels={"change_pp":"Selama − sebelum (poin indeks)"}, title="Google: seluruh DIY")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Indeks terhadap baseline hari sejenis Jan–Feb 2020; residential mengukur waktu di rumah. "
                   "Selisih poin indeks bukan % penurunan jumlah kunjungan antarperiode.")
    st.write("Pada dua wilayah contoh, porsi pencatatan dini hari lebih tinggi. Google memperlihatkan "
             "indeks taman dan retail/rekreasi lebih rendah, serta waktu di rumah lebih tinggi. "
             "Keduanya memberi sudut pandang berbeda, bukan perjalanan orang yang sama.")
    st.info("Porsi dini hari sudah naik sebelum Ramadan. Sahur dan penyesuaian rutinitas adalah hipotesis, "
            "bukan sebab yang terbukti; sampel dan pencatatan aplikasi juga dapat berubah.")
    with st.expander("Bukti dan batas interpretasi"):
        st.dataframe(focal[["kapanewon","before","during","change_pp"]].round(2))
        st.dataframe(result["google"].round(2))
        st.dataframe(result["weekly"].round(2))
        st.caption("Kegunaan: memilih jam dan kategori tempat untuk pengamatan lebih lanjut. "
                   "Bukan dasar kebutuhan transportasi atau peluang usaha; bukan seluruh Ramadan/Lebaran.")

# ---------------------------------------------------------------- Kunjungan siang (notebook 05)
with tab_visits:
    st.subheader("Kunjungan siang (08:00-17:59) antar-kapanewon")
    st.write("Satu kunjungan = device yang rumahnya di kapanewon asal terlihat di kapanewon tujuan pada jam siang, "
             "minimal sekali dalam sebulan. Tidak membedakan kerja, sekolah, belanja, atau wisata. "
             "Data Des 2021 - Feb 2022 (Mar-Apr ditandai kualitas menurun oleh sumber data).")
    month = st.selectbox("Bulan", ["Rata-rata"] + list(MONTHS), format_func=lambda m: MONTHS.get(m, m))
    odm = od if month == "Rata-rata" else od[od.month == month]
    n_months = odm.month.nunique()
    mode = st.radio("Pertanyaan", ["Dari mana pengunjung Kota Yogyakarta datang?", "Ke mana warga sebuah kapanewon pergi?",
                                   "Siapa yang mengunjungi sebuah kapanewon?"])
    ranked = ranked_origins(od)
    if mode.startswith("Dari mana"):
        cv = city_visits(odm).reset_index()
        res = (cv[cv.origin_code.isin(ranked) & ~cv.origin_code.str.startswith(CITY_KAB_CODE)]
               .groupby("origin_code")[["city_share", "city_rate"]].mean().join(names)
               .sort_values("city_share", ascending=False).head(20))
        fig = px.bar(res.iloc[::-1], x="city_share", y="label", orientation="h", color="kab_kota",
                     labels={"city_share": "Porsi kunjungan ke luar kapanewon asal yang menuju Kota (%)", "label": "",
                             "kab_kota": "Kabupaten asal"})
        fig.update_layout(height=600, margin=dict(t=20), yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        outbound = mode.startswith("Ke mana")
        pick = st.selectbox("Kapanewon", list(names.index), format_func=lambda c: names.label[c],
                            index=list(names.index).index("34.02.12"))
        key, other = ("origin_code", "dest_code") if outbound else ("dest_code", "origin_code")
        sub = odm[(odm[key] == pick) & ~odm.is_intra]
        if not outbound:
            sub = sub[sub.origin_code.isin(ranked)]
        res = (sub.groupby(other).visit_rate.sum().div(n_months) * 100).sort_values(ascending=False).head(15)
        res = res.to_frame("rate").join(names, how="left")
        xlab = ("% device rumah di kapanewon ini yang terlihat di tujuan (per bulan)" if outbound
                else "% device rumah di kapanewon asal yang terlihat di sini (per bulan)")
        fig = px.bar(res.iloc[::-1], x="rate", y="label", orientation="h", color="kab_kota",
                     labels={"rate": xlab, "label": "", "kab_kota": "Kabupaten"})
        fig.update_layout(height=520, margin=dict(t=20), yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)
        if not outbound:
            st.caption("Asal dengan < 100 device rumah di salah satu bulan tidak ditampilkan.")

# ---------------------------------------------------------------- Hari libur (notebook 04)
with tab_holiday:
    st.subheader("Kapanewon mana yang lebih ramai saat hari libur?")
    st.write("Perubahan porsi kapanewon dari total DIY pada hari libur, dibanding hari yang sama 1 dan 2 minggu "
             "sebelum dan sesudahnya (tanpa hari libur, dalam segmen panel yang sama).")
    rel = kap_holiday_shift(hourly, daily)
    hols = [d for d in daily.index[daily.is_holiday] if d in rel.index]
    choice = st.selectbox("Hari libur", ["Rata-rata semua"] + hols,
                          format_func=lambda d: d if isinstance(d, str) else f"{d:%d %b %Y} - {daily.holiday_name[d]}")
    # Average in log space, as notebook 04 does, then convert to %.
    s = rel.loc[hols].mean() if isinstance(choice, str) else rel.loc[choice]
    res = ((np.exp(s.dropna()) - 1) * 100).rename("shift").to_frame().join(names)
    res["share"] = hourly.groupby("kapanewon_code").n_maids.sum().div(hourly.n_maids.sum()).mul(100)
    show = pd.concat([res.nlargest(10, "shift"), res.nsmallest(5, "shift")]).sort_values("shift")
    fig = px.bar(show, x="shift", y="label", orientation="h", color="kab_kota",
                 hover_data={"share": ":.2f"},
                 labels={"shift": "Perubahan porsi dari DIY (%)", "label": "", "kab_kota": "Kabupaten",
                         "share": "Porsi rata-rata dari DIY (%)"})
    fig.update_layout(height=560, margin=dict(t=20), yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig, use_container_width=True)
    st.warning("Hati-hati: porsi kapanewon juga naik-turun di akhir pekan biasa. Notebook 04 membandingkan dengan "
               "akhir pekan acak; hanya Kokap dan Gedongtengen yang naiknya melebihi itu, dan di tingkat sel 500 m "
               "tidak ada sel yang menonjol. Kapanewon dengan porsi sangat kecil (Tepus, Girisubo) mudah berubah besar.")

# ---------------------------------------------------------------- Output 1 (notebook 02)
with tab_valid:
    st.subheader("Output 1: apakah JogjaPulse sejalan dengan Google?")
    st.write("Semua analisis di dashboard ini memakai JogjaPulse. Notebook 02 mengecek data itu terhadap Google, "
             "sumber yang dikumpulkan terpisah. Keduanya dibandingkan sebagai deviasi dari hari yang sama 1-2 minggu "
             "sebelum dan sesudahnya, karena angka mentah JogjaPulse dipengaruhi ukuran panel.")
    pair = daily[["dev_jp_share_gunungkidul", "dev_g_parks", "holiday_name"]].dropna(subset=["dev_jp_share_gunungkidul",
                                                                                             "dev_g_parks"])
    r = pair.dev_jp_share_gunungkidul.corr(pair.dev_g_parks, method="spearman")
    pair = pair.assign(jp=(np.exp(pair.dev_jp_share_gunungkidul) - 1) * 100,
                       kind=np.where(pair.holiday_name.notna(), "hari libur", "hari biasa"))
    fig = px.scatter(pair, x="dev_g_parks", y="jp", color="kind", hover_name=pair.index.strftime("%d %b %Y"),
                     color_discrete_map={"hari libur": G_COL, "hari biasa": GREY},
                     labels={"dev_g_parks": "Google taman: deviasi dari hari yang sama (poin)",
                             "jp": "JogjaPulse porsi Gunungkidul: deviasi (%)", "kind": ""})
    fig.update_layout(height=480, margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)
    st.metric("Korelasi Spearman (porsi Gunungkidul vs Google taman)", f"{r:.2f}", help=f"{len(pair)} hari")
    st.write("Kesepakatan lemah sampai sedang. Pada 5 dari 6 hari libur keduanya searah, tetapi belum diuji apakah "
             "kesepakatan memang lebih kuat di hari libur. Untuk sel di sekitar stasiun dan mal yang dipilih (7 dan 9 sel "
             "500 m, termasuk lingkungan sekitarnya) tidak ada kesepakatan yang jelas. Ukuran siang-malam yang diuji tidak "
             "menunjukkan beda hari kerja dan akhir pekan, jadi tidak bisa memvalidasi kategori tempat kerja Google. "
             "Selang kepercayaan dan perbandingan lain ada di notebook 02.")
