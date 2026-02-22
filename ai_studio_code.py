import xml.etree.ElementTree as ET
import re
import math
from pathlib import Path


def remove_footer_and_resize(
    input_path: str,
    output_path: str,
    footer_id: str = 'footer',
    padding: float = 10.0
):
    # 1. Register the SVG namespace to avoid modifying/corrupting the tags
    namespace = "http://www.w3.org/2000/svg"
    ET.register_namespace('', namespace)
    # ns = {'svg': namespace}

    # Parse the SVG file
    tree = ET.parse(input_path)
    root = tree.getroot()

    # 2. Find and remove the footer element
    footer_removed = False
    for parent in root.iter():
        for child in list(parent):
            if child.get('id') == footer_id:
                parent.remove(child)
                footer_removed = True
                break

    if not footer_removed:
        print(f"No <g id='{footer_id}'> found in the file.")
        return

    # 3. Calculate the new height (based on the lowest remaining element in the drawing)
    max_y = 0.0

    # Search all elements for attributes that define their vertical position
    for el in root.iter():
        y_attrs = [el.get('y'), el.get('y1'), el.get('y2'), el.get('cy')]
        for y_val in y_attrs:
            if y_val:
                try:
                    # Extract only numbers in case there are strings like "px" attached
                    y_num = float(re.search(r'[\d.]+', y_val).group())

                    # If the element has a height (like rect), add it to Y
                    height_val = el.get('height')
                    h_num = float(re.search(r'[\d.]+', height_val).group()) if height_val else 0.0

                    # Update the maximum Y-axis value
                    max_y = max(max_y, y_num + h_num)
                except (ValueError, TypeError, AttributeError):
                    continue

    # Add a bottom margin (padding) to keep it visually appealing (e.g., 15 pixels)
    new_height = math.ceil(max_y + padding)

    # 4. Update the viewBox and height attributes in the root <svg> tag
    old_viewbox = root.get('viewBox')
    if old_viewbox:
        parts = old_viewbox.split()
        if len(parts) == 4:
            parts[3] = str(new_height)  # Update the height value in the viewBox
            root.set('viewBox', " ".join(parts))

    root.set('height', str(new_height))

    # Save the new file
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print("Footer removed successfully!")
    print(f"The new height is: {new_height}px")


if __name__ == '__main__':
    dir_path = Path(__file__).parent / "examples/1"
    input_path = dir_path / 'Daily_meat_consumption_per_person,_World,_2022.svg'
    output_path = dir_path / 'cropped_gemini.svg'
    remove_footer_and_resize(
        input_path=input_path,
        output_path=output_path,
        footer_id='footer',
        padding=10.0,
    )
