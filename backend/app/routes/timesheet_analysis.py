"""
Timesheet analiz (PDF) route'ları
"""

from flask import Blueprint, request, jsonify, send_file
from io import BytesIO

from app.logger import log_error
from app.services.timesheet_analysis import create_timesheet_analysis_pdf

timesheet_analysis_bp = Blueprint("timesheet_analysis", __name__)


@timesheet_analysis_bp.route("/timesheets/analysis/pdf", methods=["POST"])
def timesheet_analysis_pdf():
    """
    PDF üretir.

    Amaç: Frontend'de takvim ekranında görünen `timesheets` datasını göndererek
    analiz/PDF'i birebir aynı verilerle üretmek.
    """
    try:
        data = request.get_json() or {}
        entries = data.get("timesheets") or []
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        user_id = data.get("user_id")
        user_name = data.get("user_name", "")

        pdf_bytes = create_timesheet_analysis_pdf(
            entries,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            user_name=user_name,
        )

        buffer = BytesIO(pdf_bytes)
        return send_file(
            buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="timesheet_analysis.pdf",
        )

    except Exception as e:
        log_error(f"Timesheet PDF analiz hatası: {e}")
        return jsonify({
            "success": False,
            "message": "PDF oluşturulurken bir hata oluştu",
        }), 500

