"""
PDF Generator
Creates PDF files from transcripts and summaries
"""

import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime


class PDFGenerator:
    def __init__(self):
        """Initialize PDF generator"""
        self.output_dir = os.path.join(
            os.path.dirname(__file__),
            '..',
            'iot-meeting-minutes',
            'recordings',
            'pdfs'
        )
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_transcript_pdf(self, transcript_file_path, session_name):
        """Create PDF from transcript file"""
        try:
            if not transcript_file_path:
                raise ValueError("Transcript file path is None or empty")
            
            if not os.path.exists(transcript_file_path):
                raise FileNotFoundError(f"Transcript file not found: {transcript_file_path}")
            
            # Read transcript file
            with open(transcript_file_path, 'r', encoding='utf-8') as f:
                transcript_content = f.read()
            
            # Create PDF file path
            pdf_filename = f"{session_name}_transcript.pdf"
            pdf_path = os.path.join(self.output_dir, pdf_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Container for PDF elements
            story = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#1a1a1a',
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor='#333333',
                spaceAfter=12,
                spaceBefore=12
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                textColor='#000000',
                spaceAfter=12,
                leading=16
            )
            
            # Add title
            story.append(Paragraph("Meeting Transcript", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Add metadata
            story.append(Paragraph(f"<b>Session:</b> {session_name}", normal_style))
            story.append(Paragraph(
                f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                normal_style
            ))
            story.append(Spacer(1, 0.3*inch))
            
            # Process transcript content
            lines = transcript_content.split('\n')
            in_content = False
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    continue
                
                # Skip header/footer markers
                if line.startswith('=') or line.startswith('Transcript:'):
                    if 'Transcript:' in line:
                        in_content = True
                    continue
                
                if not in_content:
                    continue
                
                # Check if line is a timestamp segment
                if line.startswith('[') and ']' in line:
                    # Extract timestamp and text
                    parts = line.split(']', 1)
                    if len(parts) == 2:
                        timestamp = parts[0] + ']'
                        text = parts[1].strip()
                        
                        if text:
                            # Add timestamp as heading
                            story.append(Paragraph(
                                f"<b>{timestamp}</b>",
                                heading_style
                            ))
                            # Add text
                            story.append(Paragraph(text, normal_style))
                            story.append(Spacer(1, 0.1*inch))
                else:
                    # Regular paragraph
                    if line and not line.startswith('Total') and not line.startswith('Duration'):
                        story.append(Paragraph(line, normal_style))
                        story.append(Spacer(1, 0.1*inch))
            
            # Build PDF
            doc.build(story)
            
            return pdf_path
            
        except Exception as e:
            print(f"Error creating transcript PDF: {e}")
            raise
    
    def create_summary_pdf(self, summary_file_path, session_name):
        """Create PDF from summary file"""
        try:
            if not summary_file_path:
                raise ValueError("Summary file path is None or empty")
            
            if not os.path.exists(summary_file_path):
                raise FileNotFoundError(f"Summary file not found: {summary_file_path}")
            
            # Read summary file
            with open(summary_file_path, 'r', encoding='utf-8') as f:
                summary_content = f.read()
            
            # Create PDF file path
            pdf_filename = f"{session_name}_summary.pdf"
            pdf_path = os.path.join(self.output_dir, pdf_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Container for PDF elements
            story = []
            
            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor='#1a1a1a',
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=12,
                textColor='#000000',
                spaceAfter=12,
                leading=18
            )
            
            # Add title
            story.append(Paragraph("Meeting Summary", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Add metadata
            story.append(Paragraph(f"<b>Session:</b> {session_name}", normal_style))
            story.append(Paragraph(
                f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                normal_style
            ))
            story.append(Spacer(1, 0.3*inch))
            
            # Process summary content
            lines = summary_content.split('\n')
            in_content = False
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    continue
                
                # Skip header/footer markers
                if line.startswith('=') or line.startswith('Summary:'):
                    if 'Summary:' in line:
                        in_content = True
                    continue
                
                if not in_content:
                    continue
                
                # Skip mode and other metadata
                if line.startswith('Mode:') or line.startswith('Generated:'):
                    continue
                
                # Add content
                if line:
                    story.append(Paragraph(line, normal_style))
                    story.append(Spacer(1, 0.1*inch))
            
            # Build PDF
            doc.build(story)
            
            return pdf_path
            
        except Exception as e:
            print(f"Error creating summary PDF: {e}")
            raise

