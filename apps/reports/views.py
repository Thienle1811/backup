from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from apps.medical_records.models import MedicalRecord
from .utils import build_record_pdf


@login_required
def record_pdf(request, pk):
    """Return PDF file response for a MedicalRecord."""
    record = get_object_or_404(MedicalRecord.objects.select_related("patient"), pk=pk)
    pdf_buffer: BytesIO = build_record_pdf(record)
    pdf_buffer.seek(0)
    filename = f"BA_{record.id}.pdf"
    return FileResponse(pdf_buffer, filename=filename, content_type="application/pdf")
