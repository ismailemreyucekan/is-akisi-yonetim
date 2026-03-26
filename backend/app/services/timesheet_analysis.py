from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
import os
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union


@dataclass(frozen=True)
class TimesheetLike:
    work_date: date
    project: str
    activity_type: str
    work_mode: str
    hours: float
    status: str


def _safe_hours(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except Exception:
        return 0.0


def analyze_timesheets(timesheets: Iterable[TimesheetLike]) -> Dict[str, Any]:
    total_hours = 0.0
    total_entries = 0

    by_project: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_activity: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_work_mode: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_status: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))
    by_day: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))

    for t in timesheets:
        hrs = _safe_hours(getattr(t, "hours", 0.0))
        total_hours += hrs
        total_entries += 1

        project = (getattr(t, "project", "") or "").strip() or "(Boş)"
        activity = (getattr(t, "activity_type", "") or "").strip() or "(Boş)"
        work_mode = (getattr(t, "work_mode", "") or "").strip() or "(Boş)"
        status = (getattr(t, "status", "") or "").strip() or "(Boş)"

        wd = getattr(t, "work_date", None)
        day_key = wd.isoformat() if wd else "(Tarihsiz)"

        ph, pc = by_project[project]
        by_project[project] = (ph + hrs, pc + 1)

        ah, ac = by_activity[activity]
        by_activity[activity] = (ah + hrs, ac + 1)

        wh, wc = by_work_mode[work_mode]
        by_work_mode[work_mode] = (wh + hrs, wc + 1)

        sh, sc = by_status[status]
        by_status[status] = (sh + hrs, sc + 1)

        dh, dc = by_day[day_key]
        by_day[day_key] = (dh + hrs, dc + 1)

    def to_list(d: Dict[str, Tuple[float, int]], key_name: str) -> List[Dict[str, Any]]:
        items = [{key_name: k, "hours": round(v[0], 2), "entries": v[1]} for k, v in d.items()]
        items.sort(key=lambda x: (-x["hours"], x[key_name]))
        return items

    daily = to_list(by_day, "date")
    daily.sort(key=lambda x: x["date"])

    return {
        "total_hours": round(total_hours, 2),
        "total_entries": total_entries,
        "by_project": to_list(by_project, "project"),
        "by_activity_type": to_list(by_activity, "activity_type"),
        "by_work_mode": to_list(by_work_mode, "work_mode"),
        "by_status": to_list(by_status, "status"),
        "daily": daily,
    }


def _parse_work_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value).date()
        except Exception:
            pass
        # YYYY-MM-DD formatı için hızlı deneme
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return None
    return None


def _coerce_entries(timesheets: Iterable[Union[TimesheetLike, Dict[str, Any], Any]]) -> List[TimesheetLike]:
    coerced: List[TimesheetLike] = []
    for t in timesheets:
        # SQLAlchemy model olabilir
        if hasattr(t, "work_date") and hasattr(t, "project") and hasattr(t, "activity_type"):
            work_date = _parse_work_date(getattr(t, "work_date", None))
            coerced.append(
                TimesheetLike(
                    work_date=work_date,  # type: ignore[arg-type]
                    project=str(getattr(t, "project", "") or ""),
                    activity_type=str(getattr(t, "activity_type", "") or ""),
                    work_mode=str(getattr(t, "work_mode", "") or ""),
                    hours=float(getattr(t, "hours", 0.0) or 0.0),
                    status=str(getattr(t, "status", "") or ""),
                )
            )
            continue

        if isinstance(t, dict):
            coerced.append(
                TimesheetLike(
                    work_date=_parse_work_date(t.get("work_date")) ,  # type: ignore[arg-type]
                    project=str(t.get("project") or ""),
                    activity_type=str(t.get("activity_type") or ""),
                    work_mode=str(t.get("work_mode") or ""),
                    hours=float(t.get("hours") or 0.0),
                    status=str(t.get("status") or ""),
                )
            )
            continue

        # Fallback: getattr ile dene
        work_date = _parse_work_date(getattr(t, "work_date", None))
        coerced.append(
            TimesheetLike(
                work_date=work_date,  # type: ignore[arg-type]
                project=str(getattr(t, "project", "") or ""),
                activity_type=str(getattr(t, "activity_type", "") or ""),
                work_mode=str(getattr(t, "work_mode", "") or ""),
                hours=float(getattr(t, "hours", 0.0) or 0.0),
                status=str(getattr(t, "status", "") or ""),
            )
        )

    return coerced


def analyze_timesheet_entries(timesheets: Iterable[Union[TimesheetLike, Dict[str, Any], Any]]) -> Dict[str, Any]:
    coerced = _coerce_entries(timesheets)
    return analyze_timesheets(coerced)


def create_timesheet_analysis_pdf(
    timesheets: Iterable[Union[TimesheetLike, Dict[str, Any], Any]],
    *,
    start_date: Optional[Union[str, date]] = None,
    end_date: Optional[Union[str, date]] = None,
    user_id: Optional[int] = None,
) -> bytes:
    """
    PDF üretir.

    Not: Türkçe karakterlerin bozulmaması için Windows fontunu (Tahoma/Arial/SegoeUI/Verdana)
    ReportLab'e gömüyoruz.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.graphics import renderPDF
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart

    def _parse_range(v: Optional[Union[str, date]]) -> Optional[date]:
        if v is None:
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v).date()
            except Exception:
                try:
                    return datetime.strptime(v, "%Y-%m-%d").date()
                except Exception:
                    return None
        return None

    start = _parse_range(start_date)
    end = _parse_range(end_date)

    analysis = analyze_timesheet_entries(timesheets)

    # Font kaydı (font bulunamazsa Helvetica fallback)
    font_name = "Helvetica"
    unicode_font_name = "TimesheetFont"
    candidate_fonts = [
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\verdana.ttf",
    ]
    for font_path in candidate_fonts:
        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont(unicode_font_name, font_path))
                font_name = unicode_font_name
                break
        except Exception:
            continue

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    def draw_header(title: str):
        c.setFont(font_name, 14)
        c.drawString(40, height - 50, title)
        c.setFont(font_name, 10)
        dr = f"{start.isoformat() if start else '-'} .. {end.isoformat() if end else '-'}"
        c.drawString(40, height - 68, f"Tarih araligi: {dr}")
        c.drawString(
            40,
            height - 82,
            f"Kayit sayisi: {analysis.get('total_entries', 0)}   Toplam saat: {analysis.get('total_hours', 0)}",
        )

    def make_bar_drawing(items: list, label_key: str, *, max_items: int, w: int, h: int):
        categories = [str(x.get(label_key, ""))[:18] for x in (items or [])[:max_items]]
        values = [float(x.get("hours", 0) or 0) for x in (items or [])[:max_items]]
        if not categories:
            categories = ["-"]
            values = [0]

        # Değerler 0 ise axis max'u 0 olmasın (chart bazı durumlarda bölme yapabiliyor)
        max_val = max(values) if values else 0
        if max_val <= 0:
            values = [1 for _ in values]
            max_val = 1

        chart = VerticalBarChart()
        chart.data = [values]
        chart.categoryAxis.categoryNames = categories
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max_val * 1.15
        chart.barWidth = 10
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 7
        chart.categoryAxis.labels.boxAnchor = "n"
        try:
            chart.categoryAxis.labels.fontName = font_name
        except Exception:
            pass
        try:
            chart.valueAxis.labels.fontName = font_name
        except Exception:
            pass

        chart.width = w
        chart.height = h
        drawing = Drawing(w, h)
        drawing.add(chart)
        return drawing

    # 1. sayfa: Projeler
    draw_header("Timesheet Analiz Raporu - Projeler")
    project_items = analysis.get("by_project", []) or []
    proj_chart = make_bar_drawing(project_items, "project", max_items=8, w=520, h=250)
    renderPDF.draw(proj_chart, c, 40, 520 - proj_chart.height)
    c.showPage()

    # 2. sayfa: Aktivite tipleri + Çalışma şekli
    draw_header("Timesheet Analiz Raporu - Aktivite & Çalışma Şekli")
    activity_items = analysis.get("by_activity_type", []) or []
    act_chart = make_bar_drawing(activity_items, "activity_type", max_items=8, w=520, h=200)
    renderPDF.draw(act_chart, c, 40, 340 - act_chart.height)

    work_mode_items = analysis.get("by_work_mode", []) or []
    work_chart = make_bar_drawing(work_mode_items, "work_mode", max_items=6, w=520, h=170)
    renderPDF.draw(work_chart, c, 40, 120)
    c.showPage()

    # 3. sayfa: Durumlar
    draw_header("Timesheet Analiz Raporu - Durumlar")
    status_items = analysis.get("by_status", []) or []
    st_chart = make_bar_drawing(status_items, "status", max_items=6, w=520, h=250)
    renderPDF.draw(st_chart, c, 40, 520 - st_chart.height)

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


