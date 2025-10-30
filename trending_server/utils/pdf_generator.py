from typing import Literal, Sequence
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor
from pydantic import BaseModel, HttpUrl

Category = Literal["ENTERTAINMENT", "BUSINESS", "POLITICS", "SPORTS"]


class TrendingItemModel(BaseModel):
    title: str
    summary: str
    category: Category
    audience: str
    items: list[HttpUrl]


def generate_trending_topics_pdf(trending_items: Sequence[TrendingItemModel]) -> BytesIO:
    """
    Generate a PDF from trending news data.
    Returns:
        BytesIO object containing the PDF data
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # Create story elements
    story = []

    # Set up styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#666666'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )

    story_title_style = ParagraphStyle(
        'StoryTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#2c3e50'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )

    category_style = ParagraphStyle(
        'Category',
        parent=styles['Normal'],
        fontSize=9,
        textColor=HexColor('#7f8c8d'),
        spaceAfter=4,
        fontName='Helvetica-Oblique'
    )

    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor('#34495e'),
        spaceAfter=8,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )

    source_style = ParagraphStyle(
        'Source',
        parent=styles['Normal'],
        fontSize=8,
        textColor=HexColor('#3498db'),
        spaceAfter=2,
        fontName='Helvetica',
        leftIndent=10
    )

    # Add main title
    story.append(Paragraph("Trending News Report", title_style))

    # Add date
    formatted_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    story.append(Paragraph(f"As of: {formatted_date}", date_style))
    story.append(Spacer(1, 0.2 * inch))

    # Add trending stories
    for idx, item in enumerate(trending_items, 1):
        # Add story number and title
        title = item.title or "Untitled"
        story.append(Paragraph(f"{idx}. {title}", story_title_style))

        # Add category and audience
        category = item.category or 'N/A'
        audience = item.audience or 'N/A'
        story.append(Paragraph(f"Category: {category} | Audience: {audience}", category_style))

        # Add summary
        summary = item.summary or 'No summary available'
        story.append(Paragraph(summary, summary_style))

        # Add sources
        sources = item.items or []
        if sources:
            story.append(Paragraph("<b>Sources:</b>", summary_style))
            for source_url in sources:
                # Escape special characters and create clickable link
                safe_url = source_url.encoded_string()
                story.append(Paragraph(f'• <link href="{safe_url}">{safe_url}</link>', source_style))

        # Add spacing between stories
        story.append(Spacer(1, 0.3 * inch))

        # Page break after every 3 stories (optional)
        if idx % 3 == 0 and idx < len(trending_items):
            story.append(PageBreak())

    # Build PDF
    doc.build(story)

    # Reset buffer position to beginning
    buffer.seek(0)
    return buffer
