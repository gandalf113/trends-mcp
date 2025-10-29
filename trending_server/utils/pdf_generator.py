from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.colors import HexColor


def generate_trending_news_pdf(data: dict) -> BytesIO:
    """
    Generate a PDF from trending news data.

    Args:
        data: Dictionary with 'asOf' and 'trending' keys matching the schema

    Returns:
        BytesIO object containing the PDF data
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
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
    as_of = data.get('asOf', '')
    if as_of:
        try:
            dt = datetime.fromisoformat(as_of.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%B %d, %Y at %I:%M %p %Z")
        except Exception:
            formatted_date = as_of
    else:
        formatted_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    story.append(Paragraph(f"As of: {formatted_date}", date_style))
    story.append(Spacer(1, 0.2*inch))

    # Add trending stories
    trending_items = data.get('trending', [])

    for idx, item in enumerate(trending_items, 1):
        # Add story number and title
        title = item.get('title', 'Untitled')
        story.append(Paragraph(f"{idx}. {title}", story_title_style))

        # Add category and audience
        category = item.get('category', 'N/A')
        audience = item.get('audience', 'N/A')
        story.append(Paragraph(f"Category: {category} | Audience: {audience}", category_style))

        # Add summary
        summary = item.get('summary', 'No summary available')
        story.append(Paragraph(summary, summary_style))

        # Add sources
        sources = item.get('items', [])
        if sources:
            story.append(Paragraph("<b>Sources:</b>", summary_style))
            for source_url in sources:
                # Escape special characters and create clickable link
                safe_url = source_url.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(f'• <link href="{safe_url}">{safe_url}</link>', source_style))

        # Add spacing between stories
        story.append(Spacer(1, 0.3*inch))

        # Page break after every 3 stories (optional)
        if idx % 3 == 0 and idx < len(trending_items):
            story.append(PageBreak())

    # Build PDF
    doc.build(story)

    # Reset buffer position to beginning
    buffer.seek(0)
    return buffer
