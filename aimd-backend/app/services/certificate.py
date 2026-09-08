"""
Section 65B (Indian Evidence Act, 1872) certificate generator.

IMPORTANT FRAMING: this module produces a formatted DRAFT certificate
populated with the system's own chain-of-custody and analysis data. It is
explicitly NOT a self-certifying legal instrument — Section 65B requires a
human declarant (the certifying officer) to attest to the matters in the
certificate. The generated PDF includes a signature block and is designed
to be reviewed and signed by that officer before it has any evidentiary
standing. Nothing here should be read as legal advice; consult the
department's legal cell on the exact certificate language required for a
given court.

Uses reportlab Platypus (not raw Canvas) since this is a structured
multi-section document with tables — see /mnt/skills/public/pdf/SKILL.md.
"""
import io
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.schemas import AnalyzeAudioResponse, AnalyzeMediaResponse

_STYLES = getSampleStyleSheet()

_TITLE = ParagraphStyle(
    "AIMDTitle", parent=_STYLES["Title"], fontSize=15, alignment=TA_CENTER, spaceAfter=2,
)
_SUBTITLE = ParagraphStyle(
    "AIMDSubtitle", parent=_STYLES["Normal"], fontSize=9.5, alignment=TA_CENTER,
    textColor=colors.HexColor("#374151"), spaceAfter=10,
)
_SECTION_HEADING = ParagraphStyle(
    "AIMDSection", parent=_STYLES["Heading2"], fontSize=12, spaceBefore=14, spaceAfter=6,
    textColor=colors.HexColor("#0B0F19"),
)
_BODY = ParagraphStyle("AIMDBody", parent=_STYLES["Normal"], fontSize=9.5, leading=13)
_DISCLAIMER = ParagraphStyle(
    "AIMDDisclaimer", parent=_STYLES["Normal"], fontSize=9, leading=13,
    textColor=colors.HexColor("#7C2D12"), borderColor=colors.HexColor("#F59E0B"),
    borderWidth=1, borderPadding=8, backColor=colors.HexColor("#FFFBEB"),
)
_MONO_SMALL = ParagraphStyle(
    "AIMDMono", parent=_STYLES["Normal"], fontName="Courier", fontSize=8, leading=11,
)

_TABLE_HEADER_BG = colors.HexColor("#111827")
_TABLE_HEADER_FG = colors.white
_TABLE_GRID = colors.HexColor("#9CA3AF")


def _kv_table(rows: list[tuple[str, str]]) -> Table:
    data = [[Paragraph(f"<b>{k}</b>", _BODY), Paragraph(v, _MONO_SMALL if _looks_like_hash(v) else _BODY)] for k, v in rows]
    table = Table(data, colWidths=[55 * mm, 115 * mm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, _TABLE_GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F4F6")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def _looks_like_hash(value: str) -> bool:
    return len(value) == 64 and all(c in "0123456789abcdefABCDEF" for c in value)


def _forensic_signal_table(signals: list) -> Table:
    header = [Paragraph("<b>Signal</b>", _BODY), Paragraph("<b>Score</b>", _BODY), Paragraph("<b>Description</b>", _BODY)]
    rows = [header]
    for s in signals:
        rows.append([
            Paragraph(s.name, _BODY),
            Paragraph(f"{s.score:.3f}", _MONO_SMALL),
            Paragraph(s.description, _BODY),
        ])
    table = Table(rows, colWidths=[42 * mm, 18 * mm, 110 * mm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, _TABLE_GRID),
        ("BACKGROUND", (0, 0), (-1, 0), _TABLE_HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), _TABLE_HEADER_FG),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def _integrity_row(check: dict) -> str:
    if check.get("match") is None:
        return f"UNAVAILABLE — {check.get('note', 'Original evidence file could not be re-verified.')}"
    return "MATCH — evidence file unchanged since ingestion" if check["match"] else "MISMATCH — evidence file has changed since ingestion (INVESTIGATE)"


def _media_section(job: AnalyzeMediaResponse, job_id: str, integrity: dict) -> list:
    story = [Paragraph("Exhibit — Image/Video Analysis", _SECTION_HEADING)]
    story.append(_kv_table([
        ("Job / Exhibit ID", job_id),
        ("Original filename", job.original_filename or "(not recorded)"),
        ("Media type", (job.media_type.value if job.media_type else "unknown")),
        ("Ingest timestamp (UTC)", job.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")),
        ("Analysis completed (UTC)", job.completed_at.strftime("%Y-%m-%d %H:%M:%S UTC") if job.completed_at else "n/a"),
        ("SHA-256 (at ingestion)", job.sha256_original or "n/a"),
        ("SHA-256 (recomputed at certificate generation)", integrity.get("recomputed_sha256") or "n/a"),
        ("Integrity check", _integrity_row(integrity)),
        ("Frames analyzed", str(job.frames_analyzed) if job.frames_analyzed is not None else "n/a"),
        ("System model version", job.model_version or "n/a"),
        ("Result — Threat level", (job.threat_level.value.upper() if job.threat_level else "n/a")),
        ("Result — Confidence score", f"{job.confidence_score:.4f}" if job.confidence_score is not None else "n/a"),
    ]))
    story.append(Spacer(1, 6))
    if job.forensic_signals:
        story.append(Paragraph("Forensic Signal Matrix", ParagraphStyle("h3", parent=_BODY, fontSize=10, spaceAfter=4, fontName="Helvetica-Bold")))
        story.append(_forensic_signal_table(job.forensic_signals))
    return story


def _audio_section(job: AnalyzeAudioResponse, job_id: str, integrity: dict) -> list:
    story = [Paragraph("Exhibit — Audio Analysis", _SECTION_HEADING)]
    story.append(_kv_table([
        ("Job / Exhibit ID", job_id),
        ("Original filename", job.original_filename or "(not recorded)"),
        ("Ingest timestamp (UTC)", job.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")),
        ("Analysis completed (UTC)", job.completed_at.strftime("%Y-%m-%d %H:%M:%S UTC") if job.completed_at else "n/a"),
        ("SHA-256 (at ingestion)", job.sha256_original or "n/a"),
        ("SHA-256 (recomputed at certificate generation)", integrity.get("recomputed_sha256") or "n/a"),
        ("Integrity check", _integrity_row(integrity)),
        ("Duration", f"{job.duration_seconds:.2f}s" if job.duration_seconds is not None else "n/a"),
        ("Sample rate", f"{job.sample_rate_hz} Hz" if job.sample_rate_hz else "n/a"),
        ("Segments analyzed", str(job.segments_analyzed) if job.segments_analyzed is not None else "n/a"),
        ("System model version", job.model_version or "n/a"),
        ("Result — Voice authenticity", (job.voice_authenticity.value.upper() if job.voice_authenticity else "n/a")),
        ("Result — Confidence score", f"{job.confidence_score:.4f}" if job.confidence_score is not None else "n/a"),
    ]))
    story.append(Spacer(1, 6))
    if job.forensic_signals:
        story.append(Paragraph("Forensic Signal Matrix", ParagraphStyle("h3b", parent=_BODY, fontSize=10, spaceAfter=4, fontName="Helvetica-Bold")))
        story.append(_forensic_signal_table(job.forensic_signals))
    return story


def generate_section_65b_pdf(
    *,
    case_id: str,
    officer_badge_id: str,
    officer_name: Optional[str] = None,
    notes: Optional[str] = None,
    media_job: Optional[AnalyzeMediaResponse] = None,
    media_job_id: Optional[str] = None,
    audio_job: Optional[AnalyzeAudioResponse] = None,
    audio_job_id: Optional[str] = None,
    media_integrity: Optional[dict] = None,
    audio_integrity: Optional[dict] = None,
) -> bytes:
    """
    Builds the certificate PDF in memory and returns raw bytes (callers
    stream this back as the HTTP response body, or write it to a file).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
    )

    certificate_id = str(uuid4())
    generated_at = datetime.now(timezone.utc)

    story = []
    story.append(Paragraph("AIMD — SECTION 65B CERTIFICATE", _TITLE))
    story.append(Paragraph(
        "AI Media Investigation, Detection &amp; Origin Tracing Platform — Chandigarh Police, Cyber Crime Division<br/>"
        "Certificate for Electronic Evidence under Section 65B of the Indian Evidence Act, 1872",
        _SUBTITLE,
    ))

    story.append(Paragraph("Certificate Metadata", _SECTION_HEADING))
    story.append(_kv_table([
        ("Certificate ID", certificate_id),
        ("Case ID", case_id),
        ("Generated at (UTC)", generated_at.strftime("%Y-%m-%d %H:%M:%S UTC")),
        ("Certifying officer", officer_name or "(name not recorded — see signature block)"),
        ("Officer badge ID", officer_badge_id),
        ("System", "AIMD Cyber Cell Platform v0.1.0"),
    ]))

    if media_job is not None:
        story.append(KeepTogether(_media_section(media_job, media_job_id or "n/a", media_integrity or {})))
    if audio_job is not None:
        story.append(KeepTogether(_audio_section(audio_job, audio_job_id or "n/a", audio_integrity or {})))

    if notes:
        story.append(Paragraph("Investigating Officer's Notes", _SECTION_HEADING))
        story.append(Paragraph(notes, _BODY))

    story.append(Paragraph("Disclaimer &amp; Certification Requirements", _SECTION_HEADING))
    story.append(Paragraph(
        "This certificate is system-generated as a DRAFT to assist the certifying officer under "
        "Section 65B(4) of the Indian Evidence Act, 1872. The AI analysis results above are "
        "probabilistic assessments and are NOT definitive proof of authenticity or manipulation. "
        "They must be corroborated by independent human forensic review before any evidentiary "
        "reliance. This document has no legal effect until reviewed for accuracy and signed by "
        "the certifying officer named above, in their personal capacity, attesting to the matters "
        "stated herein as required by law. This tool does not provide legal advice; consult your "
        "department's legal cell regarding the certificate language required for a specific court "
        "or proceeding.",
        _DISCLAIMER,
    ))

    story.append(Spacer(1, 22))
    story.append(Paragraph("Officer Certification", _SECTION_HEADING))
    story.append(Paragraph(
        f"I, {officer_name or '_' * 40}, holding Badge ID {officer_badge_id}, certify that, to the "
        "best of my knowledge and belief, the information in this certificate accurately describes "
        "the electronic record(s) identified above and the manner of their production by this system.",
        _BODY,
    ))
    story.append(Spacer(1, 26))
    story.append(_kv_table([
        ("Signature", "_" * 40),
        ("Date", "_" * 25),
        ("Place", "_" * 25),
    ]))

    doc.build(story)
    return buffer.getvalue()
