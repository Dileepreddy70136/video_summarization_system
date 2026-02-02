"""
Generate backend documentation PDF
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

def create_backend_pdf():
    """Create comprehensive backend documentation PDF"""
    
    output_path = os.path.join(os.path.dirname(__file__), "Backend_Documentation.pdf")
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#5f6368'),
        spaceAfter=8,
        spaceBefore=8
    )
    
    # Title
    elements.append(Paragraph("Video Summarization System", title_style))
    elements.append(Paragraph("Backend Documentation", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Overview
    elements.append(Paragraph("System Overview", heading_style))
    overview_text = """
    This is an AI-powered video summarization system that provides multiple processing options:
    <br/><br/>
    <b>Smart Edit:</b> Intelligently trims videos while preserving the original speaker's voice<br/>
    <b>Narrated Summary:</b> Creates AI-narrated video summaries with voice-over<br/>
    <b>Auto Captions:</b> Generates automatic speech-to-text captions<br/>
    <b>Visual Summary:</b> Creates keyframe-based timelapse videos
    """
    elements.append(Paragraph(overview_text, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Backend Architecture
    elements.append(Paragraph("Backend Architecture", heading_style))
    
    # Main Server
    elements.append(Paragraph("1. Main Backend Server", subheading_style))
    server_text = """
    <b>File:</b> app.py (91 lines)<br/>
    <b>Framework:</b> Flask 3.1.2<br/>
    <b>Port:</b> 5000<br/><br/>
    
    <b>Responsibilities:</b><br/>
    • Handles HTTP GET/POST requests<br/>
    • Manages file uploads to uploads/ directory<br/>
    • Routes processing requests to appropriate modules<br/>
    • Renders HTML templates with results<br/>
    • Serves processed videos and static files
    """
    elements.append(Paragraph(server_text, styles['BodyText']))
    elements.append(Spacer(1, 0.15*inch))
    
    # Processing Modules
    elements.append(Paragraph("2. Processing Modules", subheading_style))
    
    modules_data = [
        ['Module', 'Purpose', 'Lines', 'Key Technology'],
        ['auto_caption.py', 'Speech-to-text transcription', '125', 'Whisper AI, FFmpeg'],
        ['smart_edit.py', 'Intelligent video trimming', '252', 'MoviePy, NLP'],
        ['smart_cutter.py', 'AI narrated summaries', '364', 'BART, Edge-TTS'],
        ['video_summarizer.py', 'Keyframe extraction', '160', 'OpenCV, FFmpeg'],
        ['text_summarizer.py', 'Text summarization', '5', 'BART model']
    ]
    
    table = Table(modules_data, colWidths=[1.5*inch, 1.8*inch, 0.8*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Page Break
    elements.append(PageBreak())
    
    # AI Models
    elements.append(Paragraph("AI Models Used", heading_style))
    
    models_data = [
        ['Model', 'Purpose', 'Size', 'Provider'],
        ['Whisper-base', 'Speech recognition', '140 MB', 'OpenAI'],
        ['BART (facebook/bart-large-cnn)', 'Text summarization', '800 MB', 'Meta AI'],
        ['Edge-TTS (en-US-GuyNeural)', 'Text-to-speech', 'Cloud API', 'Microsoft']
    ]
    
    models_table = Table(models_data, colWidths=[2*inch, 1.8*inch, 1.2*inch, 1.5*inch])
    models_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34a853')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgreen])
    ]))
    
    elements.append(models_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Request Flow
    elements.append(Paragraph("Request Processing Flow", heading_style))
    
    flow_text = """
    <b>Example: Smart Edit Request</b><br/><br/>
    
    1. <b>User Upload:</b> User uploads video via web interface<br/><br/>
    
    2. <b>Flask Handler:</b> app.py receives POST request, saves to uploads/input.mp4<br/><br/>
    
    3. <b>Smart Edit Processing:</b><br/>
       → Calls smart_edit.create_smart_edit()<br/>
       → Step 1: Transcribe audio (Whisper AI)<br/>
       → Step 2: Analyze transcript, identify key segments<br/>
       → Step 3: Remove filler words (um, uh, like)<br/>
       → Step 4: Extract video clips WITH original audio<br/>
       → Step 5: Concatenate clips using MoviePy<br/>
       → Step 6: Write final MP4<br/><br/>
    
    4. <b>Return Results:</b> Send edited video + summary to frontend<br/><br/>
    
    5. <b>User Views:</b> Video player displays edited result
    """
    elements.append(Paragraph(flow_text, styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Dependencies
    elements.append(PageBreak())
    elements.append(Paragraph("Backend Dependencies", heading_style))
    
    deps_data = [
        ['Package', 'Version', 'Purpose'],
        ['flask', '3.1.2', 'Web framework'],
        ['transformers', '4.57.6', 'AI models (Whisper, BART)'],
        ['torch', '2.10.0', 'PyTorch backend for AI'],
        ['moviepy', '2.2.1', 'Video editing and processing'],
        ['opencv-python', 'Latest', 'Computer vision, frame extraction'],
        ['edge-tts', '7.2.7', 'Microsoft Text-to-Speech'],
        ['soundfile', 'Latest', 'Audio file I/O'],
        ['mutagen', '1.47.0', 'Audio metadata reading'],
        ['numpy', 'Latest', 'Numerical computations']
    ]
    
    deps_table = Table(deps_data, colWidths=[2*inch, 1.2*inch, 3.3*inch])
    deps_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ea4335')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightpink])
    ]))
    
    elements.append(deps_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # API Endpoints
    elements.append(Paragraph("API Endpoints", heading_style))
    
    api_text = """
    <b>GET /</b><br/>
    Returns the main web interface (index.html)<br/><br/>
    
    <b>POST /</b><br/>
    Processes video with selected options<br/>
    <b>Parameters:</b><br/>
    • video_file (file): The uploaded video<br/>
    • do_smart_edit (checkbox): Enable smart editing<br/>
    • do_narrated (checkbox): Enable AI narration<br/>
    • do_caption (checkbox): Enable captions<br/>
    • do_summary (checkbox): Enable visual summary<br/><br/>
    
    <b>GET /uploads/&lt;filename&gt;</b><br/>
    Serves processed video files<br/>
    <b>Returns:</b> MP4 video file<br/><br/>
    
    <b>GET /static/&lt;path&gt;</b><br/>
    Serves CSS, JavaScript, and static assets
    """
    elements.append(Paragraph(api_text, styles['BodyText']))
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = """
    <br/><br/>
    <i>Generated: February 1, 2026</i><br/>
    <i>System Version: 1.0</i><br/>
    <i>Python: 3.14.2 | Flask: 3.1.2</i>
    """
    elements.append(Paragraph(footer_text, styles['BodyText']))
    
    # Build PDF
    doc.build(elements)
    
    return output_path

if __name__ == "__main__":
    pdf_path = create_backend_pdf()
    print(f"PDF created successfully: {pdf_path}")
