"""
convert_readme_to_pdf.py - Converts README.md into a high-craft PDF
Uses pandoc to parse markdown and headless Chrome to generate print-ready PDF with modern styling.
"""

import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
README_MD = os.path.join(BASE_DIR, "README.md")
TEMP_HTML = os.path.join(BASE_DIR, "readme_styled.html")
OUTPUT_PDF = os.path.join(BASE_DIR, "README.pdf")

# Generate HTML body from markdown via pandoc
cmd_pandoc = ["pandoc", README_MD, "-f", "markdown", "-t", "html"]
res = subprocess.run(cmd_pandoc, capture_output=True, text=True, check=True)
body_html = res.stdout

# Wrap in modern styling
full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>LoopYard: Closed-Loop Industrial Waste & Symbiosis OS</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    @page {{
      size: A4;
      margin: 20mm 18mm 20mm 18mm;
      @bottom-right {{
        content: counter(page);
        font-family: 'Inter', sans-serif;
        font-size: 9pt;
        color: #94a3b8;
      }}
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      font-size: 10.5pt;
      line-height: 1.6;
      color: #0f172a;
      background: #ffffff;
      margin: 0;
      padding: 0;
    }}

    h1, h2, h3, h4 {{
      color: #0f172a;
      font-weight: 700;
      line-height: 1.25;
      page-break-after: avoid;
    }}

    h1 {{
      font-size: 24pt;
      border-bottom: 2px solid #059669;
      padding-bottom: 8px;
      margin-top: 0;
      margin-bottom: 12px;
      letter-spacing: -0.02em;
    }}

    h2 {{
      font-size: 15pt;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 6px;
      margin-top: 26px;
      margin-bottom: 12px;
      color: #1e293b;
    }}

    h3 {{
      font-size: 12pt;
      margin-top: 18px;
      margin-bottom: 8px;
      color: #334155;
    }}

    p {{
      margin-top: 0;
      margin-bottom: 10px;
    }}

    blockquote {{
      margin: 12px 0;
      padding: 8px 16px;
      background: #f8fafc;
      border-left: 4px solid #059669;
      color: #334155;
      font-style: italic;
    }}

    blockquote p {{
      margin: 0;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 14px 0;
      font-size: 9pt;
      page-break-inside: avoid;
    }}

    th {{
      background: #f1f5f9;
      color: #334155;
      font-weight: 700;
      text-transform: uppercase;
      font-size: 8pt;
      letter-spacing: 0.04em;
      border: 1px solid #cbd5e1;
      padding: 6px 10px;
      text-align: left;
    }}

    td {{
      border: 1px solid #e2e8f0;
      padding: 6px 10px;
      color: #1e293b;
      vertical-align: top;
    }}

    tr:nth-child(even) td {{
      background: #f8fafc;
    }}

    pre {{
      background: #0f172a;
      color: #f8fafc;
      font-family: 'JetBrains Mono', monospace;
      font-size: 8.5pt;
      line-height: 1.45;
      padding: 12px 14px;
      border-radius: 6px;
      overflow-x: auto;
      margin: 12px 0;
      page-break-inside: avoid;
    }}

    code {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 9pt;
      background: #f1f5f9;
      color: #0f172a;
      padding: 1px 4px;
      border-radius: 3px;
      border: 1px solid #e2e8f0;
    }}

    pre code {{
      background: transparent;
      color: inherit;
      padding: 0;
      border: none;
    }}

    hr {{
      border: 0;
      border-top: 1px solid #e2e8f0;
      margin: 22px 0;
    }}

    ul, ol {{
      margin-top: 0;
      margin-bottom: 12px;
      padding-left: 20px;
    }}

    li {{
      margin-bottom: 4px;
    }}

    a {{
      color: #059669;
      text-decoration: none;
    }}

    .tag {{
      display: inline-block;
      padding: 1px 6px;
      border-radius: 4px;
      font-size: 8pt;
      font-weight: 600;
    }}
  </style>
</head>
<body>
{body_html}
</body>
</html>
"""

with open(TEMP_HTML, "w", encoding="utf-8") as f:
    f.write(full_html)

# Convert to PDF via headless Google Chrome
chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
cmd_chrome = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={OUTPUT_PDF}",
    TEMP_HTML
]

subprocess.run(cmd_chrome, check=True)

# Clean up temp html
if os.path.exists(TEMP_HTML):
    os.remove(TEMP_HTML)

print(f"✓ Successfully generated PDF at: {OUTPUT_PDF}")
