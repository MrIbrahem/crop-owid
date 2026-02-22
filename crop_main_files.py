"""

"""
import sys
from pathlib import Path

from codes import claude_2, ai_studio_2

main_files_path = Path(__file__).parent / "main_files"
main_files_cropped_path = Path(__file__).parent / "main_files_cropped"

svg_files = [x for x in list(main_files_path.glob('*.svg'))]

for svg_file in svg_files:
    output_path = main_files_cropped_path / svg_file.name
    if "gemini" in sys.argv:
        ai_studio_2(
            input_path=svg_file,
            output_path=output_path,
            footer_id='footer',
            padding=10.0,
        )
    else:
        claude_2(
            input_path=svg_file,
            output_path=output_path,
            footer_id='footer',
            padding=10.0,
        )
