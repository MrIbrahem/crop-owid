"""
اريد كود بايثون لقص الجزء السفلي من ملف svg
مثال:
`<g id="footer"...`
مع تعديل ارتفاع الملف الموجود في وسم `svg` مثل:
`<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="850" height="600" viewBox="0 0 850 600"...>`
"""
from pathlib import Path

from codes import ai_studio_1, claude_1, claude_2, ai_studio_2


dir_path = Path(__file__).parent / "examples"
for sub_dir in dir_path.iterdir():
    if sub_dir.is_dir():
        print(f"Processing directory: {sub_dir}")
        svg_files = [x for x in list(sub_dir.glob('*.svg')) if "(cropped)" not in x.stem]
        for svg_file in svg_files:
            # ---
            gemini_output_path = sub_dir / "cropped_gemini.svg"
            ai_studio_2(
                input_path=svg_file,
                output_path=gemini_output_path,
                footer_id='footer',
                padding=10.0,
            )
            # ---
            claude_output_path = sub_dir / "cropped_claude.svg"
            claude_2(
                input_path=svg_file,
                output_path=claude_output_path,
                footer_id='footer',
                padding=10.0,
            )
