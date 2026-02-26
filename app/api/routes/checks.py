import io
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from app.core.database import get_db
from app.core.security import allow_all_roles, allow_admin
from app.models.check import Check
from app.models.invoice import Invoice
from app.models.user import User
from app.schemas.check import CheckResponse, GenerateCheckRequest

router = APIRouter(prefix="/api/checks", tags=["checks"])


def _to_response(chk: Check) -> CheckResponse:
    return CheckResponse(
        id=chk.id,
        check_number=chk.check_number,
        vendor_id=chk.vendor_id,
        vendor_name=chk.vendor.name if chk.vendor else None,
        amount=chk.amount,
        status=chk.status,
        issue_date=chk.issue_date,
        memo=chk.memo,
        invoice_number=chk.invoice.invoice_number if chk.invoice else None,
        created_at=chk.created_at,
    )


@router.get("", response_model=list[CheckResponse])
async def list_checks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_all_roles),
):
    result = await db.execute(
        select(Check).options(joinedload(Check.vendor), joinedload(Check.invoice)).order_by(Check.created_at.desc())
    )
    return [_to_response(c) for c in result.unique().scalars().all()]


@router.post("", response_model=CheckResponse, status_code=201)
async def generate_check(
    body: GenerateCheckRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_admin),
):
    inv_result = await db.execute(
        select(Invoice).options(joinedload(Invoice.vendor)).where(Invoice.id == body.invoice_id)
    )
    invoice = inv_result.unique().scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if invoice.status != "APPROVED":
        raise HTTPException(status_code=400, detail=f"Invoice must be APPROVED (current: {invoice.status})")
    if invoice.check_id:
        raise HTTPException(status_code=400, detail="Invoice already has a check assigned")

    max_id = (await db.execute(select(func.max(Check.id)))).scalar() or 0
    check_number = f"CHK-{max_id + 1:06d}"

    check = Check(
        check_number=check_number,
        vendor_id=invoice.vendor_id,
        amount=invoice.amount,
        status="GENERATED",
        issue_date=date.today(),
        memo=body.memo or f"Payment for invoice {invoice.invoice_number}",
    )
    db.add(check)
    await db.flush()

    invoice.check_id = check.id
    invoice.status = "CHECK_GENERATED"
    await db.flush()
    await db.refresh(check)

    result = await db.execute(
        select(Check).options(joinedload(Check.vendor), joinedload(Check.invoice)).where(Check.id == check.id)
    )
    return _to_response(result.unique().scalar_one())


@router.get("/{check_id}/pdf")
async def download_check_pdf(
    check_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_all_roles),
):
    result = await db.execute(
        select(Check).options(joinedload(Check.vendor), joinedload(Check.invoice)).where(Check.id == check_id)
    )
    check = result.unique().scalar_one_or_none()
    if not check:
        raise HTTPException(status_code=404, detail="Check not found")

    pdf_buffer = _generate_pdf(check)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="check_{check.check_number}.pdf"'},
    )


def _generate_pdf(check: Check) -> io.BytesIO:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    w, h = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, h - 1 * inch, "CHECK")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - 1 * inch, h - 1 * inch, f"Check #: {check.check_number}")
    c.drawRightString(w - 1 * inch, h - 1.2 * inch, f"Date: {check.issue_date.strftime('%m/%d/%Y')}")

    # Payee
    c.setFont("Helvetica", 11)
    c.drawString(1 * inch, h - 1.8 * inch, f"Pay to the order of: {check.vendor.name if check.vendor else 'N/A'}")
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(w - 1 * inch, h - 1.8 * inch, f"${check.amount:,.2f}")

    # Memo
    c.setFont("Helvetica", 9)
    if check.memo:
        c.drawString(1 * inch, h - 2.3 * inch, f"Memo: {check.memo}")

    # Signature line
    c.line(1 * inch, h - 2.8 * inch, w - 1 * inch, h - 2.8 * inch)
    c.setFont("Helvetica", 8)
    c.drawString(1 * inch, h - 3.0 * inch, "Authorized Signature")

    # Stub
    c.line(0.5 * inch, h - 3.5 * inch, w - 0.5 * inch, h - 3.5 * inch)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1 * inch, h - 4.0 * inch, "CHECK STUB — RETAIN FOR YOUR RECORDS")
    c.setFont("Helvetica", 9)
    y = h - 4.4 * inch
    for label, val in [
        ("Check Number", check.check_number),
        ("Date", check.issue_date.strftime("%m/%d/%Y")),
        ("Vendor", check.vendor.name if check.vendor else "N/A"),
        ("Amount", f"${check.amount:,.2f}"),
    ]:
        c.drawString(1 * inch, y, f"{label}: {val}")
        y -= 0.2 * inch
    if check.invoice:
        c.drawString(1 * inch, y, f"Invoice: {check.invoice.invoice_number}")

    c.save()
    buf.seek(0)
    return buf
