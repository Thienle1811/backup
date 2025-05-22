from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from apps.medical_records.models import MedicalRecord
from .helpers import _draw_row, _wrap_text

LINE_HEIGHT = 8  # points


def build_record_pdf(record: MedicalRecord) -> BytesIO:
    """Generate PDF for a MedicalRecord and its LabTests, return BytesIO."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left_margin = 20 * mm
    top = height - 25 * mm

    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(left_margin, top, "BỆNH ÁN")
    c.setFont("Helvetica", 12)
    c.drawString(
        left_margin, top - LINE_HEIGHT * 2, f"Bệnh nhân: {record.patient.full_name}"
    )
    c.drawString(
        left_margin,
        top - LINE_HEIGHT * 3.5,
        f"Ngày khám: {record.record_date:%d/%m/%Y}",
    )

    y = top - LINE_HEIGHT * 6

    # Diagnosis & Notes
    if record.diagnosis:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, "Chẩn đoán:")
        y -= LINE_HEIGHT * 1.2
        c.setFont("Helvetica", 11)
        for line in _wrap_text(record.diagnosis, 90):
            c.drawString(left_margin, y, line)
            y -= LINE_HEIGHT
        y -= LINE_HEIGHT

    if record.notes:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y, "Ghi chú:")
        y -= LINE_HEIGHT * 1.2
        c.setFont("Helvetica", 11)
        for line in _wrap_text(record.notes, 90):
            c.drawString(left_margin, y, line)
            y -= LINE_HEIGHT
        y -= LINE_HEIGHT

    # LabTests table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, y, "Phiếu xét nghiệm:")
    y -= LINE_HEIGHT * 1.5

    table_header = ["Loại", "Ngày", "ID"]
    col_widths = [80 * mm, 30 * mm, 20 * mm]
    _draw_row(c, left_margin, y, table_header, col_widths, header=True)
    y -= LINE_HEIGHT * 1.2

    c.setFont("Helvetica", 10)
    for lt in record.lab_tests.select_related("category"):
        row = [lt.category.name, lt.created_at.strftime("%d/%m/%Y"), str(lt.id)]
        _draw_row(c, left_margin, y, row, col_widths)
        y -= LINE_HEIGHT * 1.2
        if y < 30 * mm:
            c.showPage()
            y = height - 25 * mm

    c.showPage()
    c.save()
    return buffer
