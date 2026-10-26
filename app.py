"""STLデータ検索システム (Streamlit)。起動: streamlit run app.py"""
import os
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from scanner import list_date_folders, scan

# NASのUNCパス（製作日フォルダが並ぶ親フォルダ）。環境変数 STL_ROOT で上書き可能。
DEFAULT_ROOT = os.environ.get("STL_ROOT", r"\\NAS\stl")

st.set_page_config(page_title="STLデータ検索", page_icon="🦷", layout="wide")
st.title("🦷 STLデータ検索")


@st.cache_data(ttl=300, show_spinner=False)
def folders(root: str):
    return list_date_folders(root)


@st.cache_data(ttl=300, show_spinner="NASをスキャン中...")
def load(paths: tuple):
    rows, unparsed = [], []
    for p in paths:
        r, u = scan(p)
        rows += r
        unparsed += u
    return pd.DataFrame(rows), unparsed


with st.sidebar:
    import_option = st.radio("フォルダー取得方法", ["ZIP アップロード", "ローカルフォルダー"])
    if import_option == "ZIP アップロード":
        uploaded = st.file_uploader("検出対象フォルダー（ZIP）をドロップしてください", type=["zip"])
        if uploaded:
            import tempfile, zipfile, shutil
            tmp_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(uploaded) as z:
                z.extractall(tmp_dir)
            root = tmp_dir
        else:
            st.info("ZIP ファイルをアップロードしてください。")
            st.stop()
    else:
        folder_path = st.text_input("ローカルフォルダーのパス（フルパス）", "")
        if folder_path and os.path.isdir(folder_path):
            root = folder_path
        else:
            st.info("有効なフォルダーを入力してください。")
            st.stop()
    if st.button("🔄 再スキャン"):
        folders.clear()
        load.clear()


fmap = folders(root)
if not fmap:
    st.warning("製作日フォルダ（名前に年月日を含むフォルダ）が見つかりません。")
    st.stop()

with st.sidebar:
    st.header("製作日フォルダ")
    latest = max(fmap)
    all_days = st.checkbox("全期間を読み込む（遅い場合あり）")
    mk = st.date_input("製作日の範囲", (max(min(fmap), latest - timedelta(days=6)), latest),
                       min_value=min(fmap), max_value=latest)

if all_days:
    targets = [p for ps in fmap.values() for p in ps]
elif isinstance(mk, tuple) and len(mk) == 2:
    targets = [p for d, ps in fmap.items() if mk[0] <= d <= mk[1] for p in ps]
else:
    st.stop()

if not targets:
    st.info("該当する製作日フォルダがありません。")
    st.stop()

df, unparsed = load(tuple(sorted(targets)))
if df.empty:
    st.warning("解析可能なSTLファイルがありません。")
    st.stop()

with st.sidebar:
    st.header("絞り込み")
    clinic = st.text_input("歯科医院番号（部分一致）")
    dmin, dmax = df["due"].min(), df["due"].max()
    due = st.date_input("納期", (dmin, dmax), min_value=dmin, max_value=dmax)
    material = st.multiselect("材料", sorted(df["material"].unique()))
    shade = st.multiselect("シェード", sorted(df["shade"].unique()))
    site = st.text_input("部位（例: 16 → 16-17 も該当）")
    order = st.radio("並び順", ["更新日時が新しい順", "更新日時が古い順", "納期順"])

f = df
if clinic:
    f = f[f["clinic"].str.contains(clinic.strip())]
if isinstance(due, tuple) and len(due) == 2:
    f = f[(f["due"] >= due[0]) & (f["due"] <= due[1])]
if material:
    f = f[f["material"].isin(material)]
if shade:
    f = f[f["shade"].isin(shade)]
if site:
    s = site.strip()
    f = f[f["site"].apply(lambda v: s in v.split("-"))]
if order == "納期順":
    f = f.sort_values(["due", "serial"])
else:
    f = f.sort_values("modified", ascending=(order == "更新日時が古い順"))

st.caption(f"{len(f)} 件 / 読み込み {len(df)} 件（フォルダ {len(targets)} 個）")
cols = {"due": "納期", "material": "材料", "shade": "シェード", "clinic": "医院番号",
        "serial": "通し番号", "site": "部位", "modified": "更新日時", "size_kb": "KB", "filename": "ファイル名"}
view = f[list(cols)].rename(columns=cols).reset_index(drop=True)
event = st.dataframe(view, use_container_width=True, hide_index=True,
                     on_select="rerun", selection_mode="single-row")

sel = event.selection.rows
if sel:
    row = f.iloc[sel[0]]
    path = row["path"]
    st.subheader(row["filename"])
    st.caption("フルパス（右上のアイコンでコピー）")
    st.code(path, language=None)
    if os.path.realpath(path).startswith(os.path.realpath(root)):
        with open(path, "rb") as fh:
            st.download_button("⬇ ダウンロード", fh.read(), file_name=row["filename"],
                               mime="model/stl")
else:
    st.info("行を選択するとフルパスのコピーとダウンロードが表示されます。")

if unparsed:
    with st.expander(f"命名規則に合わないSTL: {len(unparsed)} 件"):
        st.write(unparsed[:200])
