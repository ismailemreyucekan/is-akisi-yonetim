"""
timesheet_analysis.py
─────────────────────
Mevcut kodun tamamen yeniden yazılmış versiyonu.

Public API — eski kodla birebir uyumlu:
    analyze_timesheets(timesheets)                     -> Dict
    analyze_timesheet_entries(timesheets)              -> Dict
    create_timesheet_analysis_pdf(timesheets, *, ...) -> bytes

Yeni:
    - VerticalBarChart yerine matplotlib (çok daha iyi görünüm)
    - Windows-only font yerine cross-platform Türkçe karakter desteği
    - reportlab canvas yerine Platypus (otomatik sayfa yönetimi)
    - Haftalık kırılım grafiği
    - Günlük trend çizgisi
    - Akıllı uyarı/öneri kutuları
    - user_name parametresi (opsiyonel, eski API bozulmadan)
"""

from __future__ import annotations

import io
import os
from collections import defaultdict, OrderedDict
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, Image, SimpleDocTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

# ══════════════════════════════════════════════════════════════════════════════
# 1.  FONT  — Türkçe karakter desteği (Linux / macOS / Windows)
# ══════════════════════════════════════════════════════════════════════════════
_FN = "Helvetica"
_FB = "Helvetica-Bold"


def _register_fonts() -> None:
    global _FN, _FB
    import reportlab as _rl
    rl_root = os.path.dirname(_rl.__file__)

    candidates: List[Tuple[str, str]] = [
        (
            os.path.join(rl_root, "fonts", "DejaVuSans.ttf"),
            os.path.join(rl_root, "fonts", "DejaVuSans-Bold.ttf"),
        ),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        (
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ),
        (r"C:\Windows\Fonts\arial.ttf",  r"C:\Windows\Fonts\arialbd.ttf"),
        (r"C:\Windows\Fonts\tahoma.ttf", r"C:\Windows\Fonts\tahomabd.ttf"),
    ]
    for reg_path, bold_path in candidates:
        if os.path.exists(reg_path):
            try:
                pdfmetrics.registerFont(TTFont("_TSR", reg_path))
                _FN = "_TSR"
                if os.path.exists(bold_path):
                    pdfmetrics.registerFont(TTFont("_TSB", bold_path))
                    _FB = "_TSB"
                return
            except Exception:
                continue


_register_fonts()

# ══════════════════════════════════════════════════════════════════════════════
# 2.  SABITLER
# ══════════════════════════════════════════════════════════════════════════════
PAGE_W, PAGE_H = A4
MARGIN    = 18 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

_C = {
    "primary":   "#1a1a1a",
    "secondary": "#444444",
    "muted":     "#888888",
    "border":    "#dddddd",
    "bg":        "#f7f7f7",
    "blue":      "#2563EB",
    "teal":      "#0D9488",
    "amber":     "#D97706",
    "red":       "#DC2626",
    "green":     "#16A34A",
    "purple":    "#7C3AED",
    "sky":       "#0EA5E9",
    "warn_bg":   "#fffbeb",
    "warn_brd":  "#FCD34D",
    "warn_txt":  "#92400e",
}

_PAL = [
    _C["blue"], _C["teal"], _C["amber"], _C["red"],
    _C["purple"], _C["sky"], _C["green"],
    "#F97316", "#A855F7", "#84CC16",
]

# ══════════════════════════════════════════════════════════════════════════════
# 3.  VERİ MODELİ
# ══════════════════════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class TimesheetLike:
    work_date:     date
    project:       str
    activity_type: str
    work_mode:     str
    hours:         float
    status:        str


def _safe_hours(value: Any) -> float:
    try:
        return float(value) if value is not None else 0.0
    except Exception:
        return 0.0


def _parse_work_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                pass
    return None


def _coerce_entries(
    timesheets: Iterable[Union[TimesheetLike, Dict[str, Any], Any]]
) -> List[TimesheetLike]:
    out: List[TimesheetLike] = []
    for t in timesheets:
        if isinstance(t, dict):
            g = lambda k, d=None: t.get(k, d)  # noqa: E731
        else:
            g = lambda k, d=None: getattr(t, k, d)  # noqa: E731
        out.append(TimesheetLike(
            work_date=     _parse_work_date(g("work_date")),        # type: ignore[arg-type]
            project=       str(g("project")       or "").strip() or "(Boş)",
            activity_type= str(g("activity_type") or "").strip() or "(Boş)",
            work_mode=     str(g("work_mode")     or "").strip() or "(Boş)",
            hours=         _safe_hours(g("hours")),
            status=        str(g("status")        or "").strip() or "(Boş)",
        ))
    return out

# ══════════════════════════════════════════════════════════════════════════════
# 4.  ANALİZ MOTORU
# ══════════════════════════════════════════════════════════════════════════════
def analyze_timesheets(timesheets: Iterable[TimesheetLike]) -> Dict[str, Any]:
    MESAI_SAATI = 8.0

    total_hours   = 0.0
    total_entries = 0

    by_project:   Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_activity:  Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_work_mode: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_status:    Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_day:       Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))

    for t in timesheets:
        hrs = _safe_hours(t.hours)
        total_hours   += hrs
        total_entries += 1

        for bucket, key in [
            (by_project,   t.project),
            (by_activity,  t.activity_type),
            (by_work_mode, t.work_mode),
            (by_status,    t.status),
        ]:
            h, c = bucket[key]
            bucket[key] = (h + hrs, c + 1)

        dk = t.work_date.isoformat() if t.work_date else "(Tarihsiz)"
        h, c = by_day[dk]
        by_day[dk] = (h + hrs, c + 1)

    def _lst(d: dict, key: str) -> List[Dict]:
        rows = [{key: k, "hours": round(v[0], 2), "entries": v[1]}
                for k, v in d.items()]
        rows.sort(key=lambda x: (-x["hours"], x[key]))
        return rows

    daily = [{"date": k, "hours": round(v[0], 2), "entries": v[1]}
             for k, v in by_day.items()]
    daily.sort(key=lambda x: x["date"])

    # ── Mesai uyum analizi ──────────────────────────────────────────────────
    work_days = [d for d in daily if d["date"] != "(Tarihsiz)"]
    mesai_tam   = sum(1 for d in work_days if abs(d["hours"] - MESAI_SAATI) < 0.01)
    mesai_fazla = sum(1 for d in work_days if d["hours"] > MESAI_SAATI + 0.01)
    mesai_eksik = sum(1 for d in work_days if d["hours"] < MESAI_SAATI - 0.01)
    toplam_gun  = len(work_days)

    # Ortalama eksik/fazla miktarı
    eksik_list = [MESAI_SAATI - d["hours"] for d in work_days if d["hours"] < MESAI_SAATI - 0.01]
    fazla_list = [d["hours"] - MESAI_SAATI for d in work_days if d["hours"] > MESAI_SAATI + 0.01]
    ort_eksik = round(sum(eksik_list) / len(eksik_list), 2) if eksik_list else 0.0
    ort_fazla = round(sum(fazla_list) / len(fazla_list), 2) if fazla_list else 0.0

    return {
        "total_hours":      round(total_hours, 2),
        "total_entries":    total_entries,
        "by_project":       _lst(by_project,   "project"),
        "by_activity_type": _lst(by_activity,  "activity_type"),
        "by_work_mode":     _lst(by_work_mode, "work_mode"),
        "by_status":        _lst(by_status,    "status"),
        "daily":            daily,
        "mesai": {
            "mesai_saati":  MESAI_SAATI,
            "toplam_gun":   toplam_gun,
            "tam_gun":      mesai_tam,
            "eksik_gun":    mesai_eksik,
            "fazla_gun":    mesai_fazla,
            "ort_eksik_sa": ort_eksik,
            "ort_fazla_sa": ort_fazla,
        },
    }


def analyze_timesheet_entries(
    timesheets: Iterable[Union[TimesheetLike, Dict[str, Any], Any]]
) -> Dict[str, Any]:
    return analyze_timesheets(_coerce_entries(timesheets))

# ══════════════════════════════════════════════════════════════════════════════
# 5.  GRAFİK ÜRETİCİLERİ
# ══════════════════════════════════════════════════════════════════════════════
def _to_img(fig: plt.Figure, w_mm: float, h_mm: float) -> Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150,
                bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return Image(buf, width=w_mm * mm, height=h_mm * mm)


def _clean_ax(ax: plt.Axes) -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#cccccc")
    ax.tick_params(colors="#666", labelsize=8)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#eeeeee", linewidth=0.7, linestyle="--")
    ax.xaxis.grid(False)


def _chart_hbar(
    items: List[Dict], label_key: str, title: str,
    max_items: int = 10,
    w_mm: float = 160, h_mm: float = 75,
) -> Image:
    top    = items[:max_items]
    labels = [str(x[label_key])[:32] for x in reversed(top)]
    values = [x["hours"] for x in reversed(top)]
    n      = len(labels)

    base      = np.array([37/255, 138/255, 221/255])
    bar_colors = [tuple(np.clip(base + i * 0.065, 0, 1)) for i in range(n)]

    fig_h = max(2.0, n * 0.44 + 0.6)
    fig, ax = plt.subplots(figsize=(w_mm / 25.4, fig_h))
    bars = ax.barh(labels, values, color=bar_colors, height=0.65)
    ax.bar_label(bars, fmt="%.1f sa", padding=5, fontsize=7.5, color="#555")
    ax.set_xlabel("Saat", fontsize=8, color="#999")
    _clean_ax(ax)
    ax.set_title(title, fontsize=10, pad=8, color="#1a1a1a",
                 loc="left", fontweight="bold")
    fig.tight_layout(pad=0.7)
    return _to_img(fig, w_mm, max(h_mm, fig_h * 25.4 + 8))


def _chart_donut(
    items: List[Dict], label_key: str, title: str,
    max_items: int = 7,
    w_mm: float = 78, h_mm: float = 80,
) -> Image:
    top    = items[:max_items]
    labels = [str(x[label_key])[:22] for x in top]
    values = [x["hours"] for x in top]
    clrs   = _PAL[:len(top)]
    total  = sum(values) or 1

    legend_labels = [
        f"{lb}  {v:.1f}sa  (%{v/total*100:.0f})"
        for lb, v in zip(labels, values)
    ]

    fig, ax = plt.subplots(figsize=(w_mm / 25.4, h_mm / 25.4))
    wedges, _ = ax.pie(
        values, colors=clrs, startangle=90,
        wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 1.5},
    )
    ax.legend(wedges, legend_labels,
              loc="lower center", ncol=1, fontsize=7, frameon=False,
              bbox_to_anchor=(0.5, -0.42))
    ax.set_title(title, fontsize=10, pad=6,
                 color="#1a1a1a", loc="left", fontweight="bold")
    fig.subplots_adjust(bottom=0.34)
    return _to_img(fig, w_mm, h_mm * 1.42)


def _chart_daily_trend(
    daily: List[Dict],
    w_mm: float = 160, h_mm: float = 52,
) -> Optional[Image]:
    if len(daily) < 3:
        return None

    dates = [d["date"] for d in daily]
    hours = [d["hours"] for d in daily]
    avg   = sum(hours) / len(hours)

    fig, ax = plt.subplots(figsize=(w_mm / 25.4, h_mm / 25.4))
    xs = range(len(dates))
    ax.plot(xs, hours, color=_C["blue"], linewidth=1.8,
            marker="o", markersize=4,
            markerfacecolor="white", markeredgewidth=1.5,
            markeredgecolor=_C["blue"])
    ax.fill_between(xs, hours, alpha=0.07, color=_C["blue"])
    ax.axhline(avg, color=_C["amber"], linewidth=1.0, linestyle="--",
               alpha=0.8, label=f"Günlük ort. {avg:.1f} sa")
    ax.legend(fontsize=7.5, frameon=False, loc="upper right")

    step = max(1, len(dates) // 7)
    tick_pos = list(range(0, len(dates), step))
    ax.set_xticks(tick_pos)
    ax.set_xticklabels([dates[i] for i in tick_pos],
                       rotation=30, ha="right", fontsize=7.5)
    ax.set_ylabel("Saat", fontsize=8, color="#999")
    _clean_ax(ax)
    ax.set_title("Günlük Saat Trendi", fontsize=10, pad=8,
                 color="#1a1a1a", loc="left", fontweight="bold")
    fig.tight_layout(pad=0.7)
    return _to_img(fig, w_mm, h_mm)


def _chart_weekly(
    daily: List[Dict],
    w_mm: float = 160, h_mm: float = 52,
) -> Optional[Image]:
    if len(daily) < 5:
        return None

    weeks: Dict[str, float] = OrderedDict()
    for d in daily:
        try:
            dt  = datetime.strptime(d["date"], "%Y-%m-%d").date()
            iso = dt.isocalendar()
            wk  = f"{iso[0]}-H{iso[1]:02d}"
        except Exception:
            wk = "?"
        weeks[wk] = weeks.get(wk, 0.0) + d["hours"]

    labels = list(weeks.keys())
    values = [weeks[k] for k in labels]
    avg    = sum(values) / len(values)
    bar_clrs = [_C["blue"] if v >= avg else _C["teal"] for v in values]

    fig, ax = plt.subplots(figsize=(w_mm / 25.4, h_mm / 25.4))
    bars = ax.bar(range(len(labels)), values, color=bar_clrs, width=0.6)
    ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=7.5, color="#555")
    ax.axhline(avg, color=_C["amber"], linewidth=1.1, linestyle="--",
               label=f"Haftalık ort. {avg:.1f} sa")
    ax.legend(fontsize=7.5, frameon=False)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=7.5)
    ax.set_ylabel("Saat", fontsize=8, color="#999")
    _clean_ax(ax)
    ax.set_title("Haftalık Toplam Saat", fontsize=10, pad=8,
                 color="#1a1a1a", loc="left", fontweight="bold")
    fig.tight_layout(pad=0.7)
    return _to_img(fig, w_mm, h_mm)


def _chart_mesai_uyum(
    mesai: Dict[str, Any],
    w_mm: float = 160, h_mm: float = 48,
) -> Image:
    """Tam / Eksik / Fazla mesai günlerini yatay yığılmış bar ile gösterir."""
    tam   = mesai["tam_gun"]
    eksik = mesai["eksik_gun"]
    fazla = mesai["fazla_gun"]
    total = mesai["toplam_gun"] or 1

    fig, ax = plt.subplots(figsize=(w_mm / 25.4, h_mm / 25.4))

    # Yığılmış yatay bar (tek satır)
    bar_h = 0.45
    ax.barh([0], [tam],   left=[0],           height=bar_h,
            color=_C["green"],  label=f"Tam Mesai  ({tam} gün)")
    ax.barh([0], [eksik], left=[tam],          height=bar_h,
            color=_C["amber"],  label=f"Eksik Mesai ({eksik} gün)")
    ax.barh([0], [fazla], left=[tam + eksik],  height=bar_h,
            color=_C["purple"], label=f"Fazla Mesai ({fazla} gün)")

    # Etiketleri ortaya yaz
    def _lbl(val, left):
        if val == 0:
            return
        pct = round(val / total * 100)
        ax.text(left + val / 2, 0, f"%{pct}", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")

    _lbl(tam,   0)
    _lbl(eksik, tam)
    _lbl(fazla, tam + eksik)

    ax.set_xlim(0, total)
    ax.set_yticks([])
    ax.set_xlabel("Gün sayısı", fontsize=8, color="#999")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors="#666", labelsize=8)
    ax.xaxis.grid(True, color="#eeeeee", linewidth=0.7, linestyle="--")
    ax.set_axisbelow(True)
    ax.legend(loc="lower center", ncol=3, fontsize=8, frameon=False,
              bbox_to_anchor=(0.5, -0.55))
    ax.set_title(
        f"Toplam {total} iş günü  ·  Mesai eşiği: {mesai['mesai_saati']:.0f} saat",
        fontsize=9, pad=8, color="#555", loc="left",
    )
    fig.subplots_adjust(bottom=0.38)
    return _to_img(fig, w_mm, h_mm * 1.6)

# ══════════════════════════════════════════════════════════════════════════════
# 6.  REPORTLAB YARDIMCILARI
# ══════════════════════════════════════════════════════════════════════════════
def _styles() -> Dict[str, ParagraphStyle]:
    fn, fb = _FN, _FB
    return {
        "title":  ParagraphStyle("title",  fontName=fb, fontSize=24, leading=30,
                                 textColor=colors.HexColor(_C["primary"])),
        "sub":    ParagraphStyle("sub",    fontName=fn, fontSize=12, leading=17,
                                 textColor=colors.HexColor(_C["muted"])),
        "h2":     ParagraphStyle("h2",     fontName=fb, fontSize=13, leading=18,
                                 textColor=colors.HexColor(_C["primary"]),
                                 spaceBefore=14, spaceAfter=5),
        "h3":     ParagraphStyle("h3",     fontName=fb, fontSize=10, leading=15,
                                 textColor=colors.HexColor(_C["secondary"]),
                                 spaceBefore=8, spaceAfter=3),
        "body":   ParagraphStyle("body",   fontName=fn, fontSize=9.5, leading=14,
                                 textColor=colors.HexColor(_C["secondary"])),
        "small":  ParagraphStyle("small",  fontName=fn, fontSize=8.5, leading=13,
                                 textColor=colors.HexColor(_C["muted"])),
        "right":  ParagraphStyle("right",  fontName=fn, fontSize=9, leading=13,
                                 textColor=colors.HexColor(_C["muted"]),
                                 alignment=TA_RIGHT),
        "center": ParagraphStyle("center", fontName=fn, fontSize=8.5, leading=12,
                                 textColor=colors.HexColor(_C["muted"]),
                                 alignment=TA_CENTER),
        "flag":   ParagraphStyle("flag",   fontName=fn, fontSize=9, leading=14,
                                 textColor=colors.HexColor(_C["warn_txt"])),
    }


def _metric_row(metrics: List[Tuple[str, str, str]], S: Dict) -> Table:
    n = len(metrics)
    cw = CONTENT_W / n

    label_row = [Paragraph(label, S["small"])  for label, _, _s in metrics]
    value_row = [Paragraph(f'<font name="{_FB}" size="17">{value}</font>', S["body"])
                 for _, value, _s in metrics]
    sub_row   = [Paragraph(sub, S["small"])    for _, _v, sub in metrics]

    data = [label_row, value_row, sub_row]
    t = Table(data, colWidths=[cw] * n)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor(_C["bg"])),
        ("BOX",           (0,0),(-1,-1), 0.5, colors.HexColor(_C["border"])),
        ("INNERGRID",     (0,0),(-1,-1), 0.5, colors.HexColor(_C["border"])),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
    ]))
    return t


def _detail_table(
    rows: List[Dict], label_key: str, col_label: str, S: Dict,
    max_rows: int = 15,
    total_width: float = CONTENT_W,
) -> Table:
    total = sum(r["hours"] for r in rows) or 1
    header = [
        Paragraph(col_label, S["h3"]),
        Paragraph("Saat",    S["h3"]),
        Paragraph("Giriş",   S["h3"]),
        Paragraph("Pay",     S["h3"]),
    ]
    data = [header]
    for r in rows[:max_rows]:
        pct = r["hours"] / total * 100
        data.append([
            Paragraph(str(r[label_key]), S["body"]),
            Paragraph(f'{r["hours"]:.1f}', S["body"]),
            Paragraph(str(r["entries"]),   S["body"]),
            Paragraph(f'%{pct:.0f}',       S["body"]),
        ])
    cw = [total_width * p for p in [0.50, 0.20, 0.14, 0.16]]
    t  = Table(data, colWidths=cw)
    t.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(-1,0),  _FB),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("BACKGROUND",    (0,0),(-1,0),  colors.HexColor(_C["bg"])),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),
         [colors.white, colors.HexColor(_C["bg"])]),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor(_C["border"])),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 9),
        ("ALIGN",         (1,0),(-1,-1), "CENTER"),
    ]))
    return t


def _side_by(left: Any, right: Any) -> Table:
    half = CONTENT_W / 2 - 3 * mm
    t = Table([[left, right]], colWidths=[half, CONTENT_W - half])
    t.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
        ("TOPPADDING",   (0,0),(-1,-1), 0),
        ("BOTTOMPADDING",(0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(0,-1),  4),
        ("LEFTPADDING",  (1,0),(1,-1),  4),
    ]))
    return t


def _warn_box(text: str, S: Dict) -> Table:
    t = Table([[Paragraph(f"⚠  {text}", S["flag"])]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor(_C["warn_bg"])),
        ("BOX",           (0,0),(-1,-1), 0.6, colors.HexColor(_C["warn_brd"])),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
    ]))
    return t


def _hr(story: list) -> None:
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(
        width="100%", thickness=0.5, color=colors.HexColor(_C["border"])
    ))
    story.append(Spacer(1, 3 * mm))

# ══════════════════════════════════════════════════════════════════════════════
# 7.  AKILLI UYARI ÜRETİCİ
# ══════════════════════════════════════════════════════════════════════════════
def _auto_flags(analysis: Dict[str, Any]) -> List[str]:
    flags: List[str] = []
    total = analysis["total_hours"] or 1

    for row in analysis.get("by_activity_type", []):
        pct = row["hours"] / total * 100
        act = row["activity_type"].lower()
        if any(k in act for k in ("toplantı", "meeting", "görüşme")):
            if pct > 30:
                flags.append(
                    f"Toplantı süresi yüksek (%{pct:.0f}). "
                    "Bazı toplantılar async'e (e-posta, yazılı güncelleme) alınabilir."
                )
        if any(k in act for k in ("eğitim", "training", "öğrenme", "kurs")):
            if pct < 5:
                flags.append(
                    f"Eğitim/gelişim süresi düşük (%{pct:.0f}). "
                    "Haftada en az 2 saat gelişim bloğu planlanabilir."
                )

    proj_count = len(analysis.get("by_project", []))
    if proj_count >= 6:
        flags.append(
            f"Bu dönemde {proj_count} farklı projede çalışılmış. "
            "Çok fazla proje değişimi bağlam kaybına yol açabilir."
        )

    daily_hours = [d["hours"] for d in analysis.get("daily", [])]
    if len(daily_hours) >= 5:
        avg = float(np.mean(daily_hours))
        std = float(np.std(daily_hours))
        if avg > 0 and std / avg > 0.55:
            flags.append(
                f"Günlük saatlerde belirgin dalgalanma var "
                f"(ort. {avg:.1f} sa, std sapma {std:.1f} sa). "
                "Daha tutarlı bir çalışma ritmi verimliliği artırabilir."
            )
    return flags

# ══════════════════════════════════════════════════════════════════════════════
# 8.  ANA PDF FONKSİYONU
# ══════════════════════════════════════════════════════════════════════════════
def create_timesheet_analysis_pdf(
    timesheets: Iterable[Union[TimesheetLike, Dict[str, Any], Any]],
    *,
    start_date: Optional[Union[str, date]] = None,
    end_date:   Optional[Union[str, date]] = None,
    user_id:    Optional[int] = None,
    user_name:  str = "",
) -> bytes:
    """
    Timesheet verilerinden analiz PDF'i üretir, bytes döner.
    Eski API ile birebir uyumludur; user_name opsiyonel olarak eklenmiştir.
    """
    def _pd(v: Any) -> Optional[date]:
        if v is None:
            return None
        if isinstance(v, date):
            return v
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(str(v), fmt).date()
            except ValueError:
                pass
        return None

    start = _pd(start_date)
    end   = _pd(end_date)

    analysis = analyze_timesheet_entries(timesheets)
    flags    = _auto_flags(analysis)

    total_h = analysis["total_hours"]
    total_e = analysis["total_entries"]
    by_proj = analysis["by_project"]
    by_act  = analysis["by_activity_type"]
    by_mode = analysis["by_work_mode"]
    daily   = analysis["daily"]
    mesai   = analysis["mesai"]

    S       = _styles()
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN,  bottomMargin=MARGIN,
        title="Timesheet Analiz Raporu",
    )
    story: list = []

    # ── Başlık ─────────────────────────────────────────────────────────────
    hdr = Table(
        [[
            Paragraph("Timesheet Analiz Raporu", S["title"]),
            Paragraph(f"Oluşturulma<br/>{now_str}", S["right"]),
        ]],
        colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35],
    )
    hdr.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "BOTTOM"),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    story.append(hdr)

    meta: List[str] = []
    if user_name:
        meta.append(user_name)
    if start and end:
        meta.append(f"{start.strftime('%d.%m.%Y')} – {end.strftime('%d.%m.%Y')}")
    elif start:
        meta.append(f"{start.strftime('%d.%m.%Y')} itibaren")
    if meta:
        story.append(Paragraph("  ·  ".join(meta), S["small"]))

    _hr(story)

    # ── Özet metrik kartları ───────────────────────────────────────────────
    top_proj = by_proj[0]["project"][:20]      if by_proj else "-"
    top_act  = by_act[0]["activity_type"][:20] if by_act  else "-"
    top_mode = by_mode[0]["work_mode"][:20]    if by_mode else "-"
    story.append(_metric_row([
        ("Toplam Saat",       f"{total_h:.1f} sa", f"{total_e} giriş"),
        ("En Çok Proje",      top_proj,             ""),
        ("En Çok Aktivite",   top_act,              ""),
        ("En Çok Çal. Şekli", top_mode,             ""),
    ], S))
    story.append(Spacer(1, 3 * mm))

    # ── Mesai uyum metrik özeti ─────────────────────────────────────────────
    tam_pct  = round(mesai["tam_gun"]   / mesai["toplam_gun"] * 100) if mesai["toplam_gun"] else 0
    eks_pct  = round(mesai["eksik_gun"] / mesai["toplam_gun"] * 100) if mesai["toplam_gun"] else 0
    faz_pct  = round(mesai["fazla_gun"] / mesai["toplam_gun"] * 100) if mesai["toplam_gun"] else 0
    story.append(_metric_row([
        ("Tam Mesai Günleri",  f"{mesai['tam_gun']} gün",   f"%{tam_pct}  •  (={mesai['mesai_saati']:.0f} sa)"),
        ("Eksik Mesai Günleri", f"{mesai['eksik_gun']} gün", f"%{eks_pct}  •  ort. {mesai['ort_eksik_sa']:.1f} sa eksik"),
        ("Fazla Mesai Günleri", f"{mesai['fazla_gun']} gün", f"%{faz_pct}  •  ort. {mesai['ort_fazla_sa']:.1f} sa fazla"),
        ("Toplam İş Günü",      f"{mesai['toplam_gun']} gün", ""),
    ], S))
    story.append(Spacer(1, 5 * mm))

    # ── Grafik 1: Proje bazlı yatay bar ───────────────────────────────────
    story.append(Paragraph("Proje Bazlı Saat Dağılımı", S["h2"]))
    story.append(_chart_hbar(
        by_proj, "project", "Projeye göre saat",
        max_items=10, w_mm=CONTENT_W / mm,
    ))
    story.append(Spacer(1, 5 * mm))

    # ── Grafik 2: Aktivite + Çalışma şekli donutları ──────────────────────
    story.append(Paragraph("Aktivite Tipi ve Çalışma Şekli", S["h2"]))
    d_act  = _chart_donut(by_act,  "activity_type", "Aktivite Tipi",
                          w_mm=(CONTENT_W / mm) / 2 - 3)
    d_mode = _chart_donut(by_mode, "work_mode",     "Çalışma Şekli",
                          w_mm=(CONTENT_W / mm) / 2 - 3)
    story.append(_side_by(d_act, d_mode))
    story.append(Spacer(1, 5 * mm))

    # ── Grafik 3: Günlük trend ─────────────────────────────────────────────
    g_trend = _chart_daily_trend(daily, w_mm=CONTENT_W / mm)
    if g_trend:
        story.append(Paragraph("Günlük Saat Trendi", S["h2"]))
        story.append(g_trend)
        story.append(Spacer(1, 5 * mm))

    # ── Grafik 4: Haftalık toplam ──────────────────────────────────────────
    g_weekly = _chart_weekly(daily, w_mm=CONTENT_W / mm)
    if g_weekly:
        story.append(Paragraph("Haftalık Toplam", S["h2"]))
        story.append(g_weekly)
        story.append(Spacer(1, 5 * mm))

    # ── Grafik 5: Mesai uyum çubuğu ───────────────────────────────────────
    if mesai["toplam_gun"] > 0:
        story.append(Paragraph("Mesai Uyum Analizi (Günlük 8 Saat)", S["h2"]))
        story.append(_chart_mesai_uyum(mesai, w_mm=CONTENT_W / mm))
        story.append(Spacer(1, 5 * mm))

    # ── Detay tabloları ────────────────────────────────────────────────────
    story.append(Paragraph("Detay Tablolar", S["h2"]))
    story.append(Paragraph("Proje", S["h3"]))
    story.append(_detail_table(by_proj, "project", "Proje Adı", S))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Aktivite Tipi", S["h3"]))
    story.append(_detail_table(by_act, "activity_type", "Aktivite", S))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Çalışma Şekli", S["h3"]))
    story.append(_detail_table(by_mode, "work_mode", "Çalışma Şekli", S))
    story.append(Spacer(1, 5 * mm))

    # ── Uyarı / öneri kutuları ─────────────────────────────────────────────
    if flags:
        story.append(Paragraph("Öneriler & Dikkat Edilecekler", S["h2"]))
        for flag in flags:
            story.append(_warn_box(flag, S))
            story.append(Spacer(1, 2 * mm))
        story.append(Spacer(1, 3 * mm))

    # ── Footer ─────────────────────────────────────────────────────────────
    _hr(story)
    story.append(Paragraph(
        f"Bu rapor otomatik olarak oluşturulmuştur  ·  {now_str}",
        S["center"],
    ))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# 9.  DEMO
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import random
    from datetime import timedelta

    random.seed(7)
    projects   = ["Müşteri A Portalı", "İç Platform v2", "API Entegrasyon",
                  "Mobil Uygulama", "DevOps / CI-CD", "Raporlama Modülü",
                  "Güvenlik Denetimi"]
    activities = ["Geliştirme", "Toplantı", "Eğitim", "Kod İnceleme",
                  "Dokümantasyon", "Test & QA"]
    modes      = ["Uzaktan", "Ofis", "Hibrit"]
    statuses   = ["Onaylandı", "Beklemede", "Reddedildi"]

    entries = []
    start_d = date(2025, 3, 1)
    for i in range(92):
        d = start_d + timedelta(days=i)
        if d.weekday() >= 5:
            continue
        for _ in range(random.randint(1, 5)):
            entries.append({
                "work_date":     d.isoformat(),
                "project":       random.choice(projects),
                "activity_type": random.choice(activities),
                "work_mode":     random.choice(modes),
                "hours":         round(random.uniform(0.5, 4.5), 1),
                "status":        random.choices(
                    statuses, weights=[70, 25, 5]
                )[0],
            })

    pdf_bytes = create_timesheet_analysis_pdf(
        entries,
        start_date=date(2025, 3, 1),
        end_date=date(2025, 5, 31),
        user_name="Ali Yilmaz",
    )

    out = "/mnt/user-data/outputs/timesheet_analysis.pdf"
    with open(out, "wb") as f:
        f.write(pdf_bytes)
    print(f"PDF olusturuldu: {out}  ({len(pdf_bytes) // 1024} KB)")