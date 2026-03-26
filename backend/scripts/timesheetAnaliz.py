"""
Timesheet analiz scripti.

Bu dosyadaki analiz mantığı, backend içinde `app/services/timesheet_analysis.py` ile aynıdır.
Script, hızlıca DB'den çekip JSON çıktı almak için kullanılabilir.
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Timesheet
from app.services.timesheet_analysis import analyze_timesheets


def run(user_id=None, start_date=None, end_date=None, include_drafts=True):
    app = create_app()
    with app.app_context():
        query = Timesheet.query
        if user_id:
            query = query.filter(Timesheet.identity_id == int(user_id))
        if start_date:
            query = query.filter(Timesheet.work_date >= start_date)
        if end_date:
            query = query.filter(Timesheet.work_date <= end_date)
        if not include_drafts:
            query = query.filter(Timesheet.status != 'Taslak')

        rows = query.order_by(Timesheet.work_date.asc(), Timesheet.id.asc()).all()
        return analyze_timesheets(rows)


if __name__ == "__main__":
    # Örnek kullanım:
    # python scripts/timesheetAnaliz.py 1
    user_id = sys.argv[1] if len(sys.argv) > 1 else None
    result = run(user_id=user_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))