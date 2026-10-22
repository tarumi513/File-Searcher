"""STLファイルのスキャンとファイル名解析。"""
import os
import re
from datetime import datetime

# 区切り文字（_ - 空白 .）に対応。命名規則が変わったらここだけ修正する。
SEP = r"[_\-\s.]"
# 部位は 14 や 16-17 のようにハイフン連結で複数指定可
PATTERN = re.compile(
    rf"^(?P<due>\d{{8}}){SEP}(?P<material>[A-Za-z]+){SEP}(?P<shade>[A-Za-z0-9]+){SEP}"
    rf"(?P<clinic>\d{{5}}){SEP}(?P<serial>\d{{3}}){SEP}(?P<site>\d{{2}}(?:-\d{{2}})*)(?:{SEP}.*)?$",
    re.IGNORECASE,
)

# 製作日フォルダ名（20261022 / 2026-10-22 / 2026_10_22 など）
FOLDER_DATE = re.compile(r"(\d{4})\D?(\d{2})\D?(\d{2})")


def folder_date(name: str):
    m = FOLDER_DATE.search(name)
    if not m:
        return None
    try:
        return datetime(*map(int, m.groups())).date()
    except ValueError:
        return None


def list_date_folders(root: str):
    """root直下の製作日フォルダを {日付: [パス,...]} で返す。日付不明フォルダは除外。"""
    out = {}
    for e in os.scandir(root):
        if e.is_dir():
            d = folder_date(e.name)
            if d:
                out.setdefault(d, []).append(e.path)
    return out


def parse_name(stem: str):
    m = PATTERN.match(stem)
    if not m:
        return None
    d = m.groupdict()
    try:
        d["due"] = datetime.strptime(d["due"], "%Y%m%d").date()
    except ValueError:
        return None
    d["material"] = d["material"].upper()
    d["shade"] = d["shade"].upper()
    return d


def scan(root: str):
    """root配下のSTLを走査。(解析成功の行リスト, 解析失敗のパスリスト)を返す。"""
    rows, unparsed = [], []
    for dirpath, _, files in os.walk(root):
        for f in files:
            stem, ext = os.path.splitext(f)
            if ext.lower() != ".stl":
                continue
            path = os.path.join(dirpath, f)
            meta = parse_name(stem)
            if meta is None:
                unparsed.append(path)
                continue
            try:
                st = os.stat(path)
            except OSError:
                continue
            meta.update(
                path=path,
                filename=f,
                modified=datetime.fromtimestamp(st.st_mtime),
                size_kb=round(st.st_size / 1024, 1),
            )
            rows.append(meta)
    return rows, unparsed
