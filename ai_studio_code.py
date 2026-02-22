import xml.etree.ElementTree as ET
import re
import math


def remove_footer_and_resize(input_file, output_file):
    # 1. Register the SVG namespace to avoid modifying/corrupting the tags
    namespace = "http://www.w3.org/2000/svg"
    ET.register_namespace('', namespace)
    # ns = {'svg': namespace}

    # Parse the SVG file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # 2. Find and remove the footer element
    footer_removed = False
    for parent in root.iter():
        for child in list(parent):
            if child.get('id') == 'footer':
                parent.remove(child)
                footer_removed = True
                break

    if not footer_removed:
        print("No <g id='footer'> found in the file.")
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
    padding = 15
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
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print("Footer removed successfully!")
    print(f"The new height is: {new_height}px")


# Run the code
# Put the paths for the original and output files here
remove_footer_and_resize('original_chart.svg', 'modified_chart.svg')
