from datetime import datetime
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def add_centered_text(paragraph, text, bold=False, size=12):
    """Thêm text được căn giữa vào paragraph"""
    run = paragraph.add_run(text)
    run.font.name = 'Times New Roman'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    run.font.size = Pt(size)
    run.font.bold = bold
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return run

def add_right_text(paragraph, text, bold=False, size=12):
    """Thêm text được căn phải vào paragraph"""
    run = paragraph.add_run(text)
    run.font.name = 'Times New Roman'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    run.font.size = Pt(size)
    run.font.bold = bold
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    return run

def add_left_text(paragraph, text, bold=False, size=12):
    """Thêm text được căn trái vào paragraph"""
    run = paragraph.add_run(text)
    run.font.name = 'Times New Roman'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
    run.font.size = Pt(size)
    run.font.bold = bold
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return run

def export_labtest_to_word(labtest):
    """Xuất kết quả xét nghiệm ra file Word"""
    doc = Document()
    
    # Thiết lập margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(1.27)
        section.bottom_margin = Cm(1.27)
        section.left_margin = Cm(1.27)
        section.right_margin = Cm(1.27)

    # Thêm logo
    if os.path.exists('static/images/logo.png'):
        doc.add_picture('static/images/logo.png', width=Cm(2))
        last_paragraph = doc.paragraphs[-1]
        last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Header
    p = doc.add_paragraph()
    add_centered_text(p, "Y KHOA UNG BƯỚU CẦN THƠ", bold=True, size=14)
    
    p = doc.add_paragraph()
    add_centered_text(p, "PHÒNG XÉT NGHIỆM MEDIONCON", bold=True, size=14)
    
    p = doc.add_paragraph()
    add_centered_text(p, "Địa chỉ: Số 10, ĐS 5, Tổ 17, KV Bình Thường B, P. Long Tuyền, Q. Bình Thủy, TPCT.", size=12)
    
    p = doc.add_paragraph()
    add_centered_text(p, "Điện thoại: 0917.575656.", size=12)
    
    p = doc.add_paragraph()
    add_centered_text(p, "Wed: Ykhoaungbuoucantho.com.vn.", size=12)
    
    p = doc.add_paragraph()
    add_centered_text(p, "Email.CSKH.MIDEONCO@GMAIL.COM.", size=12)

    # Thông tin phiếu
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_right_text(p, f"STT: {datetime.now().strftime('%d/%m/%Y')}-{labtest.id}", size=12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_right_text(p, f"Ngày đăng ký: {labtest.created_at.strftime('%d/%m/%Y - %H:%M') if labtest.created_at else 'N/A'}", size=12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_right_text(p, f"Giờ xuất file: {datetime.now().strftime('%d/%m/%Y - %H:%M')}", size=12)

    # Tiêu đề
    p = doc.add_paragraph()
    add_centered_text(p, "KẾT QUẢ XÉT NGHIỆM", bold=True, size=14)
    doc.add_paragraph()

    # Thông tin bệnh nhân
    p = doc.add_paragraph()
    add_left_text(p, f"Họ tên: {labtest.patient.full_name}", size=12)
    
    p = doc.add_paragraph()
    add_left_text(p, f"Ngày tháng năm sinh: {labtest.patient.date_of_birth.strftime('%d/%m/%Y') if labtest.patient.date_of_birth else 'N/A'}", size=12)

    # Bảng kết quả
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header của bảng
    header_cells = table.rows[0].cells
    headers = ['XÉT NGHIỆM', 'KẾT QUẢ', 'KHOẢNG THAM CHIẾU', 'ĐƠN VỊ']
    for i, header in enumerate(headers):
        header_cells[i].text = header
        header_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in header_cells[i].paragraphs[0].runs:
            run.font.bold = True
            run.font.size = Pt(12)
            run.font.name = 'Times New Roman'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')

    # Thêm category name
    row_cells = table.add_row().cells
    row_cells[0].merge(row_cells[3])
    row_cells[0].text = labtest.category.name
    row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in row_cells[0].paragraphs[0].runs:
        run.font.bold = True
        run.font.size = Pt(12)
        run.font.name = 'Times New Roman'
        run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')

    # Thêm kết quả
    for result in labtest.results.select_related('item').order_by('item__order'):
        row_cells = table.add_row().cells
        row_cells[0].text = result.item.name
        row_cells[1].text = result.value
        row_cells[2].text = result.item.reference_range
        row_cells[3].text = result.item.unit
        
        for cell in row_cells:
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in cell.paragraphs[0].runs:
                run.font.size = Pt(12)
                run.font.name = 'Times New Roman'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')

    doc.add_paragraph()

    # Footer
    p = doc.add_paragraph()
    add_centered_text(p, "Kết quả đã được kiểm duyệt /QA", size=12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_right_text(p, f"TP. Cần Thơ, ngày {datetime.now().strftime('%d')} tháng {datetime.now().strftime('%m')} năm {datetime.now().strftime('%Y')}", size=12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_right_text(p, "PHÒNG XÉT NGHIỆM", size=12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_right_text(p, "(Ký, đóng dấu và ghi rõ họ tên)", size=12)

    # Lưu file
    filename = f"labtest_{labtest.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc.save(filename)
    
    # Update last print date
    labtest.last_print_date = datetime.now()
    labtest.save()
    
    return filename 