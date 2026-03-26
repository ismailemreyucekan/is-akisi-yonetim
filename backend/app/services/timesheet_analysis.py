"""
timesheet_analysis.py  —  Otomatik Analiz ve Rapor Sistemi
===========================================================
Public API (değişmedi):
    analyze_timesheets(timesheets)                -> Dict
    analyze_timesheet_entries(timesheets)         -> Dict
    create_timesheet_analysis_pdf(timesheets, *) -> bytes

PDF Yapısı:
    Sayfa 1 – Yönetici Özeti (Executive Summary)
    Sayfa 2 – Detaylı Görsel Analizler
    Sayfa 3 – Anomali & İK Notları (Otomatik Yorumlar)
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
import matplotlib.patches as mpatches
import numpy as np

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, Image, SimpleDocTemplate, PageBreak,
    Paragraph, Spacer, Table, TableStyle,
)

# ══════════════════════════════════════════════════════════════════════════════
# 1. FONT
# ══════════════════════════════════════════════════════════════════════════════
_FN = "Helvetica"
_FB = "Helvetica-Bold"

def _register_fonts() -> None:
    global _FN, _FB
    import reportlab as _rl
    rl_root = os.path.dirname(_rl.__file__)
    candidates: List[Tuple[str, str]] = [
        (os.path.join(rl_root, "fonts", "DejaVuSans.ttf"),
         os.path.join(rl_root, "fonts", "DejaVuSans-Bold.ttf")),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
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
# 2. SABITLER
# ══════════════════════════════════════════════════════════════════════════════
PAGE_W, PAGE_H = A4
MARGIN    = 18 * mm
CONTENT_W = PAGE_W - 2 * MARGIN
MESAI_SAATI = 8.0

_C = {
    "primary":   "#1a1a1a",
    "secondary": "#374151",
    "muted":     "#6B7280",
    "border":    "#E5E7EB",
    "bg":        "#F9FAFB",
    "bg2":       "#F3F4F6",
    "blue":      "#2563EB",
    "teal":      "#0D9488",
    "amber":     "#D97706",
    "red":       "#DC2626",
    "red_light": "#FEE2E2",
    "green":     "#16A34A",
    "green_light":"#DCFCE7",
    "purple":    "#7C3AED",
    "sky":       "#0EA5E9",
    "warn_bg":   "#FFFBEB",
    "warn_brd":  "#FCD34D",
    "warn_txt":  "#92400E",
    "info_bg":   "#EFF6FF",
    "info_brd":  "#BFDBFE",
    "info_txt":  "#1E40AF",
    "accent":    "#4F46E5",
    "header_bg": "#1E293B",
}

_PAL = [
    _C["blue"], _C["teal"], _C["amber"], _C["red"],
    _C["purple"], _C["sky"], _C["green"],
    "#F97316", "#A855F7", "#84CC16", "#EC4899", "#14B8A6",
]

# ══════════════════════════════════════════════════════════════════════════════
# 3. VERİ MODELİ
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
            g = lambda k, d=None: t.get(k, d)
        else:
            g = lambda k, d=None: getattr(t, k, d)
        out.append(TimesheetLike(
            work_date=     _parse_work_date(g("work_date")),
            project=       str(g("project")       or "").strip() or "(Boş)",
            activity_type= str(g("activity_type") or "").strip() or "(Boş)",
            work_mode=     str(g("work_mode")     or "").strip() or "(Boş)",
            hours=         _safe_hours(g("hours")),
            status=        str(g("status")        or "").strip() or "(Boş)",
        ))
    return out

# ══════════════════════════════════════════════════════════════════════════════
# 4. ANALİZ MOTORU
# ══════════════════════════════════════════════════════════════════════════════
def analyze_timesheets(timesheets: Iterable[TimesheetLike]) -> Dict[str, Any]:
    total_hours   = 0.0
    total_entries = 0
    approved_hours = 0.0

    by_project:   Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_activity:  Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_work_mode: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_status:    Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_day:       Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    leave_days:   List[Dict] = []

    for t in timesheets:
        hrs = _safe_hours(t.hours)
        total_hours   += hrs
        total_entries += 1
        if t.status in ("Onaylandı", "Approved"):
            approved_hours += hrs

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

        # İzin tespiti
        if "izin" in t.project.lower() or "izin" in t.activity_type.lower():
            leave_days.append({
                "date":    dk,
                "hours":   hrs,
                "project": t.project,
                "type":    t.activity_type,
            })

    def _lst(d: dict, key: str) -> List[Dict]:
        rows = [{key: k, "hours": round(v[0], 2), "entries": v[1]}
                for k, v in d.items()]
        rows.sort(key=lambda x: (-x["hours"], x[key]))
        return rows

    daily = [{"date": k, "hours": round(v[0], 2), "entries": v[1]}
             for k, v in by_day.items()]
    daily.sort(key=lambda x: x["date"])

    # Mesai uyum
    work_days   = [d for d in daily if d["date"] != "(Tarihsiz)"]
    toplam_gun  = len(work_days)
    mesai_tam   = sum(1 for d in work_days if abs(d["hours"] - MESAI_SAATI) < 0.01)
    mesai_fazla = sum(1 for d in work_days if d["hours"] > MESAI_SAATI + 0.01)
    mesai_eksik = sum(1 for d in work_days if d["hours"] < MESAI_SAATI - 0.01)
    fazla_toplam = sum(d["hours"] - MESAI_SAATI for d in work_days if d["hours"] > MESAI_SAATI + 0.01)
    eksik_list   = [MESAI_SAATI - d["hours"] for d in work_days if d["hours"] < MESAI_SAATI - 0.01]
    fazla_list   = [d["hours"] - MESAI_SAATI for d in work_days if d["hours"] > MESAI_SAATI + 0.01]
    ort_eksik    = round(sum(eksik_list) / len(eksik_list), 2) if eksik_list else 0.0
    ort_fazla    = round(sum(fazla_list) / len(fazla_list), 2) if fazla_list else 0.0
    avg_daily    = round(total_hours / toplam_gun, 2) if toplam_gun else 0.0

    # En yoğun gün
    max_day = max(work_days, key=lambda d: d["hours"]) if work_days else None

    return {
        "total_hours":      round(total_hours, 2),
        "total_entries":    total_entries,
        "approved_hours":   round(approved_hours, 2),
        "avg_daily_hours":  avg_daily,
        "max_day":          max_day,
        "by_project":       _lst(by_project,   "project"),
        "by_activity_type": _lst(by_activity,  "activity_type"),
        "by_work_mode":     _lst(by_work_mode, "work_mode"),
        "by_status":        _lst(by_status,    "status"),
        "daily":            daily,
        "leave_days":       sorted(leave_days, key=lambda x: x["date"]),
        "mesai": {
            "mesai_saati":   MESAI_SAATI,
            "toplam_gun":    toplam_gun,
            "tam_gun":       mesai_tam,
            "eksik_gun":     mesai_eksik,
            "fazla_gun":     mesai_fazla,
            "fazla_toplam":  round(fazla_toplam, 2),
            "ort_eksik_sa":  ort_eksik,
            "ort_fazla_sa":  ort_fazla,
        },
    }

def analyze_timesheet_entries(
    timesheets: Iterable[Union[TimesheetLike, Dict[str, Any], Any]]
) -> Dict[str, Any]:
    return analyze_timesheets(_coerce_entries(timesheets))

# ══════════════════════════════════════════════════════════════════════════════
# 5. GRAFİK ÜRETİCİLERİ
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
    ax.spines[["left", "bottom"]].set_color("#D1D5DB")
    ax.tick_params(colors="#6B7280", labelsize=8)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#F3F4F6", linewidth=0.8, linestyle="--")
    ax.xaxis.grid(False)


def _chart_donut(
    items: List[Dict], label_key: str, title: str,
    max_items: int = 7, w_mm: float = 78, h_mm: float = 78,
) -> Image:
    top    = items[:max_items]
    labels = [str(x[label_key])[:24] for x in top]
    values = [x["hours"] for x in top]
    clrs   = _PAL[:len(top)]
    total  = sum(values) or 1

    legend_labels = [
        f"{lb}  {v:.1f}sa (%{v/total*100:.0f})"
        for lb, v in zip(labels, values)
    ]
    fig, ax = plt.subplots(figsize=(w_mm / 25.4, h_mm / 25.4))
    wedges, _ = ax.pie(
        values, colors=clrs, startangle=90, radius=0.9,
        wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 2},
    )
    ax.legend(wedges, legend_labels,
              loc="upper center", ncol=1, fontsize=7, frameon=False,
              bbox_to_anchor=(0.5, -0.05))
    ax.set_title(title, fontsize=10, pad=10,
                 color=_C["primary"], loc="center", fontweight="bold")
    fig.subplots_adjust(bottom=0.45, top=0.85)
    return _to_img(fig, w_mm, h_mm * 1.6)


def _chart_daily_bar_threshold(
    daily: List[Dict], w_mm: float = 160, h_mm: float = 60,
) -> Optional[Image]:
    """Günlük sütun grafik — 8s eşiği kırmızı çizgi, fazla mesai çubukları farklı renk."""
    if len(daily) < 2:
        return None

    dates = [d["date"] for d in daily]
    hours = [d["hours"] for d in daily]
    xs    = list(range(len(dates)))

    bar_clrs = [
        _C["red"] if h > MESAI_SAATI + 0.01
        else (_C["green"] if abs(h - MESAI_SAATI) < 0.01 else _C["blue"])
        for h in hours
    ]

    fig, ax = plt.subplots(figsize=(w_mm / 25.4, h_mm / 25.4))
    bars = ax.bar(xs, hours, color=bar_clrs, width=0.65, zorder=3)
    ax.axhline(MESAI_SAATI, color=_C["amber"], linewidth=1.5,
               linestyle="--", label=f"Standart Mesai ({MESAI_SAATI:.0f} sa)", zorder=4)

    # Fazla mesai çubuklarına etiket
    for bar, h in zip(bars, hours):
        if h > MESAI_SAATI + 0.01:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    h + 0.15, f"{h:.1f}", ha="center", va="bottom",
                    fontsize=6.5, color=_C["red"], fontweight="bold")

    step = max(1, len(dates) // 8)
    tick_pos = list(range(0, len(dates), step))
    ax.set_xticks(tick_pos)
    ax.set_xticklabels([dates[i][5:] for i in tick_pos],
                       rotation=45, ha="right", fontsize=7.5)
    ax.set_ylabel("Saat", fontsize=8, color="#999")

    # Limit the y-axis a bit higher to give room for numbers
    max_h = max(hours) if hours else MESAI_SAATI
    ax.set_ylim(0, max(max_h * 1.2, MESAI_SAATI * 1.2))

    legend_patches = [
        mpatches.Patch(color=_C["red"],   label="Fazla Mesai"),
        mpatches.Patch(color=_C["green"], label="Tam Mesai"),
        mpatches.Patch(color=_C["blue"],  label="Normal"),
    ]
    handles, lbl = ax.get_legend_handles_labels()
    
    # Legend'i tablonun üstüne koyalım (barlarla çakışmasın)
    ax.legend(handles=legend_patches + handles,
              fontsize=7.5, frameon=False, loc="lower center",
              bbox_to_anchor=(0.5, 1.02), ncol=4)
    _clean_ax(ax)
    
    # Title'ı biraz daha yukarı alalım
    fig.text(0.02, 0.95, "Günlük Çalışma Saatleri & Fazla Mesai Analizi",
             fontsize=10, color=_C["primary"], fontweight="bold")
    
    fig.subplots_adjust(top=0.8, bottom=0.2)
    return _to_img(fig, w_mm, h_mm * 1.2)


def _chart_activity_hbar(
    items: List[Dict], w_mm: float = 160, h_mm: float = 65,
) -> Image:
    top    = items[:8]
    labels = [str(x["activity_type"])[:30] for x in reversed(top)]
    values = [x["hours"] for x in reversed(top)]
    n      = len(labels)
    clrs   = [_PAL[i % len(_PAL)] for i in range(n)]

    fig_h = max(2.5, n * 0.5 + 0.8)
    fig, ax = plt.subplots(figsize=(w_mm / 25.4, fig_h))
    bars = ax.barh(labels, values, color=clrs, height=0.6)
    ax.bar_label(bars, fmt="%.1f sa", padding=5, fontsize=7.5, color="#555")
    ax.set_xlabel("Saat", fontsize=8, color="#999")
    
    # Y-axis yazıların kesilmesini engelle
    if values:
        ax.set_xlim(0, max(values) * 1.25)

    _clean_ax(ax)
    ax.set_title("Görev Türü Analizi",
                 fontsize=10, pad=12, color=_C["primary"],
                 loc="left", fontweight="bold")
    fig.subplots_adjust(left=0.3, right=0.95, top=0.85, bottom=0.15)
    return _to_img(fig, w_mm, max(h_mm, fig_h * 25.4 + 8))


def _chart_mesai_stacked(mesai: Dict, w_mm: float = 160, h_mm: float = 40) -> Image:
    tam   = mesai["tam_gun"]
    eksik = mesai["eksik_gun"]
    fazla = mesai["fazla_gun"]
    total = mesai["toplam_gun"] or 1

    fig, ax = plt.subplots(figsize=(w_mm / 25.4, h_mm / 25.4))
    bar_h = 0.45
    ax.barh([0], [tam],   left=[0],          height=bar_h, color=_C["green"])
    ax.barh([0], [eksik], left=[tam],         height=bar_h, color=_C["amber"])
    ax.barh([0], [fazla], left=[tam + eksik], height=bar_h, color=_C["red"])

    def _lbl(val, left, color):
        if val == 0:
            return
        pct = round(val / total * 100)
        ax.text(left + val / 2, 0, f"%{pct}\n({val}g)",
                ha="center", va="center", fontsize=8.5,
                color="white", fontweight="bold", linespacing=1.3)

    _lbl(tam,   0,          _C["green"])
    _lbl(eksik, tam,        _C["amber"])
    _lbl(fazla, tam + eksik, _C["red"])

    ax.set_xlim(0, total * 1.05)
    ax.set_yticks([])
    ax.set_xlabel("Gün", fontsize=8, color="#999")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#D1D5DB")
    ax.tick_params(colors="#6B7280", labelsize=8)

    legend_patches = [
        mpatches.Patch(color=_C["green"], label=f"Tam Mesai ({tam} gün)"),
        mpatches.Patch(color=_C["amber"], label=f"Eksik ({eksik} gün)"),
        mpatches.Patch(color=_C["red"],   label=f"Fazla ({fazla} gün)"),
    ]
    ax.legend(handles=legend_patches, loc="upper center", ncol=3,
              fontsize=8, frameon=False, bbox_to_anchor=(0.5, -0.4))
    fig.subplots_adjust(bottom=0.4)
    return _to_img(fig, w_mm, h_mm * 1.7)

# ══════════════════════════════════════════════════════════════════════════════
# 6. REPORTLAB YARDIMCILARI
# ══════════════════════════════════════════════════════════════════════════════
def _styles() -> Dict[str, ParagraphStyle]:
    fn, fb = _FN, _FB
    return {
        "title":   ParagraphStyle("title",   fontName=fb, fontSize=22, leading=28,
                                  textColor=colors.white),
        "title2":  ParagraphStyle("title2",  fontName=fb, fontSize=16, leading=22,
                                  textColor=colors.HexColor(_C["primary"])),
        "sub":     ParagraphStyle("sub",     fontName=fn, fontSize=11, leading=16,
                                  textColor=colors.white),
        "sub2":    ParagraphStyle("sub2",    fontName=fn, fontSize=10, leading=15,
                                  textColor=colors.HexColor(_C["muted"])),
        "h2":      ParagraphStyle("h2",      fontName=fb, fontSize=13, leading=18,
                                  textColor=colors.HexColor(_C["primary"]),
                                  spaceBefore=14, spaceAfter=5),
        "h3":      ParagraphStyle("h3",      fontName=fb, fontSize=10, leading=15,
                                  textColor=colors.HexColor(_C["secondary"]),
                                  spaceBefore=8, spaceAfter=3),
        "body":    ParagraphStyle("body",    fontName=fn, fontSize=9.5, leading=14,
                                  textColor=colors.HexColor(_C["secondary"])),
        "small":   ParagraphStyle("small",   fontName=fn, fontSize=8.5, leading=13,
                                  textColor=colors.HexColor(_C["muted"])),
        "right":   ParagraphStyle("right",   fontName=fn, fontSize=9, leading=13,
                                  textColor=colors.white, alignment=TA_RIGHT),
        "center":  ParagraphStyle("center",  fontName=fn, fontSize=8.5, leading=12,
                                  textColor=colors.HexColor(_C["muted"]),
                                  alignment=TA_CENTER),
        "warn":    ParagraphStyle("warn",    fontName=fn, fontSize=9, leading=14,
                                  textColor=colors.HexColor(_C["warn_txt"])),
        "info":    ParagraphStyle("info",    fontName=fn, fontSize=9, leading=14,
                                  textColor=colors.HexColor(_C["info_txt"])),
        "good":    ParagraphStyle("good",    fontName=fn, fontSize=9, leading=14,
                                  textColor=colors.HexColor(_C["green"])),
        "note_h":  ParagraphStyle("note_h",  fontName=fb, fontSize=9.5, leading=14,
                                  textColor=colors.HexColor(_C["primary"])),
    }


def _hr(story: list, color: str = _C["border"]) -> None:
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(
        width="100%", thickness=0.6, color=colors.HexColor(color)
    ))
    story.append(Spacer(1, 3 * mm))


def _kpi_card(label: str, value: str, sub: str,
              bg: str = _C["bg"], accent: str = _C["blue"],
              S: Dict = None) -> Table:
    """Tek bir KPI kartı."""
    fn, fb = _FN, _FB
    s_lbl = ParagraphStyle("kl", fontName=fn, fontSize=8, leading=12,
                            textColor=colors.HexColor(_C["muted"]))
    s_val = ParagraphStyle("kv", fontName=fb, fontSize=18, leading=22,
                            textColor=colors.HexColor(accent))
    s_sub = ParagraphStyle("ks", fontName=fn, fontSize=8, leading=12,
                            textColor=colors.HexColor(_C["muted"]))
    data = [[
        Paragraph(label, s_lbl),
        Paragraph(value, s_val),
        Paragraph(sub,   s_sub),
    ]]
    t = Table(data, colWidths=[None])
    cw = CONTENT_W / 4
    t = Table([[
        Paragraph(label, s_lbl),
        Paragraph(value, s_val),
        Paragraph(sub,   s_sub),
    ]], colWidths=[cw])
    return t


def _kpi_row(cards: List[Tuple[str, str, str, str]], S: Dict) -> Table:
    """
    cards: [(label, value, sub, accent_color), ...]
    Yan yana KPI kartları.
    """
    fn, fb = _FN, _FB
    n  = len(cards)
    cw = CONTENT_W / n
    cells = []
    for label, value, sub, accent in cards:
        s_lbl = ParagraphStyle(f"l{label}", fontName=fn, fontSize=8, leading=11,
                               textColor=colors.HexColor(_C["muted"]))
        s_val = ParagraphStyle(f"v{label}", fontName=fb, fontSize=17, leading=21,
                               textColor=colors.HexColor(accent))
        s_sub = ParagraphStyle(f"s{label}", fontName=fn, fontSize=7.5, leading=11,
                               textColor=colors.HexColor(_C["muted"]))
        cells.append([
            Paragraph(label, s_lbl),
            Paragraph(value, s_val),
            Paragraph(sub,   s_sub),
        ])

    t = Table([cells], colWidths=[cw] * n)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(_C["bg"])),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor(_C["border"])),
        ("INNERGRID",     (0, 0), (-1, -1), 0.4, colors.HexColor(_C["border"])),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    return t


def _note_box(icon: str, text: str, style_key: str, bg: str,
              brd: str, S: Dict) -> Table:
    t = Table([[Paragraph(f"{icon}  {text}", S[style_key])]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(bg)),
        ("BOX",           (0, 0), (-1, -1), 0.6, colors.HexColor(brd)),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
    ]))
    return t


def _detail_table(
    rows: List[Dict], label_key: str, col_label: str, S: Dict,
    max_rows: int = 15, total_width: float = CONTENT_W,
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
        ("FONTNAME",      (0, 0), (-1, 0),  _FB),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor(_C["bg2"])),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1),
         [colors.white, colors.HexColor(_C["bg"])]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor(_C["border"])),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 9),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
    ]))
    return t


def _side_by(left: Any, right: Any, gap_mm: float = 4) -> Table:
    half = CONTENT_W / 2 - gap_mm * mm
    t = Table([[left, right]], colWidths=[half, CONTENT_W - half])
    t.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1),  gap_mm * mm / 2),
        ("LEFTPADDING",  (1, 0), (1, -1),  gap_mm * mm / 2),
    ]))
    return t

# ══════════════════════════════════════════════════════════════════════════════
# 7. OTOMATİK IK YORUMLARI
# ══════════════════════════════════════════════════════════════════════════════
def _auto_remarks(analysis: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """
    (icon, text, style_key) üçlüleri döner.
    style_key: 'warn' | 'info' | 'good'
    """
    notes: List[Tuple[str, str, str]] = []
    total   = analysis["total_hours"] or 1
    mesai   = analysis["mesai"]
    daily   = analysis["daily"]
    max_day = analysis.get("max_day")

    # En yoğun gün
    if max_day:
        notes.append((
            "📌",
            f"{max_day['date']} tarihli gün, {max_day['hours']:.1f} saatlik çalışma"
            " ile dönemin en yoğun günü olmuştur.",
            "note_h",
        ))

    # Aktivite yorum
    for row in analysis.get("by_activity_type", []):
        pct = row["hours"] / total * 100
        act = row["activity_type"].lower()
        if any(k in act for k in ("geliştirme", "development", "coding")):
            if pct >= 60:
                notes.append((
                    "✅",
                    f"Geliştirme aktiviteleri toplam sürenin %{pct:.0f}'ini oluşturmaktadır."
                    " Bu, teknik odaklanmanın yüksek olduğunu gösterir.",
                    "good",
                ))
        if any(k in act for k in ("toplantı", "meeting")):
            if pct > 30:
                notes.append((
                    "⚠️",
                    f"Toplantı süresi toplam çalışmanın %{pct:.0f}'ini kapsıyor."
                    " Bazı toplantıların async (yazılı güncelleme) formatına taşınması önerilebilir.",
                    "warn",
                ))
        if any(k in act for k in ("eğitim", "training", "öğrenme")):
            if pct < 5:
                notes.append((
                    "ℹ️",
                    f"Eğitim/gelişim aktiviteleri toplam sürenin yalnızca %{pct:.0f}'ini oluşturuyor."
                    " Haftada en az 2 saat gelişim bloğu planlanabilir.",
                    "info",
                ))

    # Fazla mesai
    if mesai["fazla_gun"] > 0:
        notes.append((
            "⚠️",
            f"{mesai['fazla_gun']} iş gününde standart mesai ({MESAI_SAATI:.0f} sa)"
            f" aşılmıştır. Toplam fazla mesai: {mesai['fazla_toplam']:.1f} saat."
            " İş kanunu uyumluluğu ve tükenmişlik riski açısından takip önerilir.",
            "warn",
        ))

    # Haftalık dalgalanma
    if len(daily) >= 5:
        hours_list = [d["hours"] for d in daily]
        avg = float(np.mean(hours_list))
        std = float(np.std(hours_list))
        if avg > 0 and std / avg > 0.55:
            notes.append((
                "📊",
                f"Günlük çalışma saatlerinde belirgin dalgalanma gözlemlenmektedir"
                f" (ort. {avg:.1f} sa, std sapma {std:.1f} sa)."
                " Daha tutarlı bir çalışma ritmi verimliliği artırabilir.",
                "warn",
            ))
        elif avg > 0 and std / avg <= 0.30:
            notes.append((
                "✅",
                f"Haftalık çalışma saatleri stabil bir seyir izlemektedir"
                f" (ort. {avg:.1f} sa, sapma {std:.1f} sa).",
                "good",
            ))

    # Onay oranı
    approved_pct = analysis["approved_hours"] / total * 100 if total > 0 else 0
    if approved_pct >= 95:
        notes.append((
            "✅",
            f"Toplam çalışmanın %{approved_pct:.0f}'i onaylanmış durumda."
            " Bu, yüksek bir güven endeksi sağlamaktadır.",
            "good",
        ))
    elif approved_pct < 50:
        notes.append((
            "⚠️",
            f"Toplam çalışmanın yalnızca %{approved_pct:.0f}'i onaylanmış."
            " Onay bekleyen girişlerin güncellenmesi önerilir.",
            "warn",
        ))

    # İzin
    leave = analysis.get("leave_days", [])
    if leave:
        total_leave_h = sum(l["hours"] for l in leave)
        notes.append((
            "📅",
            f"İzin: {len(leave)} giriş, toplam {total_leave_h:.1f} saat izin kullanılmıştır.",
            "info",
        ))

    # Proje çeşitliliği
    proj_count = len(analysis.get("by_project", []))
    if proj_count >= 6:
        notes.append((
            "ℹ️",
            f"Bu dönemde {proj_count} farklı projede çalışılmıştır."
            " Çok fazla proje geçişi bağlam kaybına yol açabilir.",
            "info",
        ))

    return notes

# ══════════════════════════════════════════════════════════════════════════════
# 8. ANA PDF FONKSİYONU
# ══════════════════════════════════════════════════════════════════════════════
def create_timesheet_analysis_pdf(
    timesheets: Iterable[Union[TimesheetLike, Dict[str, Any], Any]],
    *,
    start_date: Optional[Union[str, date]] = None,
    end_date:   Optional[Union[str, date]] = None,
    user_id:    Optional[int] = None,
    user_name:  str = "",
) -> bytes:
    """Timesheet verilerinden 3 sayfalık analiz PDF'i üretir, bytes döner."""

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
    remarks  = _auto_remarks(analysis)

    total_h    = analysis["total_hours"]
    total_e    = analysis["total_entries"]
    approved_h = analysis["approved_hours"]
    avg_daily  = analysis["avg_daily_hours"]
    by_proj    = analysis["by_project"]
    by_act     = analysis["by_activity_type"]
    by_mode    = analysis["by_work_mode"]
    daily      = analysis["daily"]
    mesai      = analysis["mesai"]
    leave_days = analysis["leave_days"]
    max_day    = analysis.get("max_day")

    S       = _styles()
    now_str = datetime.now().strftime("%d.%m.%Y %H:%M")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Timesheet Analiz Raporu",
    )
    story: list = []

    # ─────────────────────────────────────────────────────────────────────────
    # SAYFA 1 — YÖNETİCİ ÖZETİ (Executive Summary)
    # ─────────────────────────────────────────────────────────────────────────

    # Koyu başlık banner
    period_str = ""
    if start and end:
        period_str = f"{start.strftime('%d.%m.%Y')} – {end.strftime('%d.%m.%Y')}"
    elif start:
        period_str = f"{start.strftime('%d.%m.%Y')} itibaren"

    banner_data = [[
        Paragraph("Timesheet Analiz Raporu", S["title"]),
        Paragraph(f"Oluşturulma<br/>{now_str}", S["right"]),
    ]]
    banner = Table(banner_data, colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(_C["header_bg"])),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(banner)
    story.append(Spacer(1, 2 * mm))

    # Çalışan & dönem bilgisi
    meta_parts = []
    if user_name:
        meta_parts.append(f"<b>Çalışan:</b> {user_name}")
    if period_str:
        meta_parts.append(f"<b>Dönem:</b> {period_str}")
    if meta_parts:
        story.append(Paragraph("  ·  ".join(meta_parts), S["sub2"]))
    story.append(Spacer(1, 4 * mm))

    # ── KPI Kartları – Satır 1: Genel Özet ────────────────────────────────
    top_proj = by_proj[0]["project"][:22] if by_proj else "—"
    story.append(Paragraph("Genel Performans Özeti", S["h2"]))
    story.append(_kpi_row([
        ("Toplam Çalışma Süresi",  f"{total_h:.1f} sa",   f"{total_e} giriş",         _C["blue"]),
        ("Ortalama Günlük Süre",   f"{avg_daily:.1f} sa",  f"{mesai['toplam_gun']} iş günü", _C["teal"]),
        ("Onaylanan Saat",         f"{approved_h:.1f} sa", f"%{round(approved_h/total_h*100) if total_h else 0} oranında",  _C["green"]),
        ("En Çok Zaman Ayrılan",   top_proj,               "Proje",                    _C["purple"]),
    ], S))
    story.append(Spacer(1, 3 * mm))

    # ── KPI Kartları – Satır 2: Mesai Analizi ─────────────────────────────
    story.append(Paragraph("Mesai Uyum Analizi  (Eşik: 8 saat/gün)", S["h2"]))
    tam_pct = round(mesai["tam_gun"]   / mesai["toplam_gun"] * 100) if mesai["toplam_gun"] else 0
    eks_pct = round(mesai["eksik_gun"] / mesai["toplam_gun"] * 100) if mesai["toplam_gun"] else 0
    faz_pct = round(mesai["fazla_gun"] / mesai["toplam_gun"] * 100) if mesai["toplam_gun"] else 0
    story.append(_kpi_row([
        ("Tam Mesai Günleri",   f"{mesai['tam_gun']} gün",
         f"%{tam_pct}",                             _C["green"]),
        ("Eksik Mesai Günleri", f"{mesai['eksik_gun']} gün",
         f"%{eks_pct}  ·  ort. {mesai['ort_eksik_sa']:.1f} sa eksik", _C["amber"]),
        ("Fazla Mesai Günleri", f"{mesai['fazla_gun']} gün",
         f"%{faz_pct}  ·  ort. {mesai['ort_fazla_sa']:.1f} sa fazla", _C["red"]),
        ("Toplam Fazla Mesai",  f"{mesai['fazla_toplam']:.1f} sa",
         "dönem toplamı",                           _C["purple"]),
    ], S))
    story.append(Spacer(1, 4 * mm))

    # ── Proje Bazlı Özet Tablo ────────────────────────────────────────────
    story.append(Paragraph("Proje Bazlı Dağılım", S["h2"]))
    story.append(_detail_table(by_proj, "project", "Proje", S, max_rows=10))
    story.append(Spacer(1, 3 * mm))

    # ── İzin Özeti ────────────────────────────────────────────────────────
    if leave_days:
        story.append(Paragraph("İzin ve Devamsızlık", S["h2"]))
        total_leave_h = sum(l["hours"] for l in leave_days)
        lv_header = [
            Paragraph("Tarih",     S["h3"]),
            Paragraph("Süre",      S["h3"]),
            Paragraph("Tür",       S["h3"]),
        ]
        lv_data = [lv_header]
        for lv in leave_days:
            lv_data.append([
                Paragraph(lv["date"],  S["body"]),
                Paragraph(f'{lv["hours"]:.1f} sa', S["body"]),
                Paragraph(lv["type"],  S["body"]),
            ])
        lv_cw = [CONTENT_W * p for p in [0.35, 0.25, 0.40]]
        lv_t  = Table(lv_data, colWidths=lv_cw)
        lv_t.setStyle(TableStyle([
            ("FONTNAME",      (0, 0), (-1, 0),  _FB),
            ("FONTSIZE",      (0, 0), (-1, -1), 9),
            ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor(_C["bg2"])),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1),
             [colors.white, colors.HexColor(_C["bg"])]),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor(_C["border"])),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 9),
        ]))
        story.append(lv_t)
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(
            f"Toplam: {len(leave_days)} izin girişi  ·  {total_leave_h:.1f} saat",
            S["small"]
        ))

    # ═════════════════════════════════════════════════════════════════════════
    # SAYFA 2 — DETAYLI GÖRSEL ANALİZLER
    # ═════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    # Sayfa 2 başlığı
    p2_banner_data = [[
        Paragraph("Detaylı Görsel Analizler", S["title"]),
        Paragraph(f"Sayfa 2  ·  {now_str}", S["right"]),
    ]]
    p2_banner = Table(p2_banner_data, colWidths=[CONTENT_W * 0.7, CONTENT_W * 0.3])
    p2_banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(_C["accent"])),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
    ]))
    story.append(p2_banner)
    story.append(Spacer(1, 5 * mm))

    # Sol: Proje donut  |  Sağ: Aktivite donut
    story.append(Paragraph("Proje ve Görev Kırılımı", S["h2"]))
    half_mm = (CONTENT_W / mm) / 2 - 4
    d_proj = _chart_donut(by_proj, "project",        "Projeye Göre Dağılım", w_mm=half_mm)
    d_act  = _chart_donut(by_act,  "activity_type",  "Aktivite Türüne Göre", w_mm=half_mm)
    story.append(_side_by(d_proj, d_act))
    story.append(Spacer(1, 5 * mm))

    # Fazla mesai & eşik grafiği
    story.append(Paragraph("Fazla Mesai ve İş Yükü Analizi", S["h2"]))
    g_bar = _chart_daily_bar_threshold(daily, w_mm=CONTENT_W / mm)
    if g_bar:
        story.append(g_bar)
    else:
        story.append(Paragraph("(Yeterli günlük veri yok)", S["small"]))
    story.append(Spacer(1, 5 * mm))

    # Görev türü analizi (yatay bar)
    story.append(Paragraph("Görev Türü Analizi", S["h2"]))
    story.append(_chart_activity_hbar(by_act, w_mm=CONTENT_W / mm))
    story.append(Spacer(1, 5 * mm))

    # Mesai uyum yığılmış bar
    if mesai["toplam_gun"] > 0:
        story.append(Paragraph("Mesai Uyum Dağılımı", S["h2"]))
        story.append(_chart_mesai_stacked(mesai, w_mm=CONTENT_W / mm))
        story.append(Spacer(1, 5 * mm))

    # Alt: Aktivite + Çalışma şekli detay tabloları
    story.append(Paragraph("Detay Tablolar", S["h2"]))
    _hw = CONTENT_W / 2 - 3 * mm
    story.append(_side_by(
        _detail_table(by_act,  "activity_type", "Aktivite Türü",   S, total_width=_hw),
        _detail_table(by_mode, "work_mode",     "Çalışma Şekli",   S, total_width=_hw),
    ))

    # ═════════════════════════════════════════════════════════════════════════
    # SAYFA 3 — ANOMALİ & İK NOTLARI
    # ═════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    p3_banner_data = [[
        Paragraph("Anomali & İK Notları", S["title"]),
        Paragraph(f"Sayfa 3  ·  {now_str}", S["right"]),
    ]]
    p3_banner = Table(p3_banner_data, colWidths=[CONTENT_W * 0.7, CONTENT_W * 0.3])
    p3_banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(_C["teal"])),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
    ]))
    story.append(p3_banner)
    story.append(Spacer(1, 5 * mm))

    story.append(Paragraph("Otomatik Sistem Yorumları", S["h2"]))
    story.append(Paragraph(
        "Aşağıdaki notlar sistem tarafından veriye dayalı olarak otomatik üretilmiştir.",
        S["small"]
    ))
    story.append(Spacer(1, 3 * mm))

    # Renk kodlu notlar
    style_map = {
        "warn":   (_C["warn_bg"],   _C["warn_brd"],  "warn"),
        "info":   (_C["info_bg"],   _C["info_brd"],  "info"),
        "good":   (_C["green_light"], _C["green"],   "good"),
        "note_h": (_C["bg"],        _C["border"],    "note_h"),
    }
    if remarks:
        for icon, text, sk in remarks:
            bg, brd, actual_sk = style_map.get(sk, (_C["bg"], _C["border"], "body"))
            story.append(_note_box(icon, text, actual_sk, bg, brd, S))
            story.append(Spacer(1, 2 * mm))
    else:
        story.append(_note_box(
            "ℹ️", "Bu dönem için otomatik yorum üretilecek yeterli veri bulunamadı.",
            "info", _C["info_bg"], _C["info_brd"], S
        ))

    story.append(Spacer(1, 5 * mm))

    # Onay durumu detayı
    story.append(Paragraph("Onay Durumu Özeti", S["h2"]))
    story.append(_detail_table(
        analysis["by_status"], "status", "Durum", S, max_rows=10
    ))
    story.append(Spacer(1, 5 * mm))

    # ── Footer ────────────────────────────────────────────────────────────
    _hr(story)
    footer_parts = [f"Bu rapor otomatik olarak oluşturulmuştur  ·  {now_str}"]
    if user_name:
        footer_parts.append(user_name)
    story.append(Paragraph("  ·  ".join(footer_parts), S["center"]))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


# ══════════════════════════════════════════════════════════════════════════════
# 9. DEMO
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    import random
    from datetime import timedelta

    random.seed(7)
    projects   = ["Mainframe", "BMC Platform", "API Entegrasyon",
                  "Mobil Uygulama", "DevOps / CI-CD", "İzin"]
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
        for _ in range(random.randint(1, 4)):
            entries.append({
                "work_date":     d.isoformat(),
                "project":       random.choice(projects),
                "activity_type": random.choice(activities),
                "work_mode":     random.choice(modes),
                "hours":         round(random.uniform(0.5, 4.5), 1),
                "status":        random.choices(statuses, weights=[70, 25, 5])[0],
            })

    pdf_bytes = create_timesheet_analysis_pdf(
        entries,
        start_date=date(2025, 3, 1),
        end_date=date(2025, 5, 31),
        user_name="Ali Yilmaz",
    )
    out = "timesheet_analysis_demo.pdf"
    with open(out, "wb") as f:
        f.write(pdf_bytes)
    print(f"PDF olusturuldu: {out}  ({len(pdf_bytes) // 1024} KB)")