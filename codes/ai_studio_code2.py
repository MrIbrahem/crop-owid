from pathlib import Path
import re
import xml.etree.ElementTree as ET
import math


def get_min_y_of_element(element) -> float:
    """
    Extract the minimum y value from an SVG element and all its descendants.
    Used to determine the exact starting position of the footer.
    """
    min_y = float('inf')

    return min_y if min_y != float('inf') else None


def get_max_y_of_element(element) -> float:
    """
    Get the maximum y+height value from an SVG element and all its descendants.
    Used to calculate the actual bottom edge of the remaining content.
    """
    max_y = 0.0

    y_attrs = [element.get('y'), element.get('y1'), element.get('y2'), element.get('cy')]
    for y_val in y_attrs:
        if y_val:
            try:
                # Extract only numbers in case there are strings like "px" attached
                y_val = float(re.search(r'[\d.-]+', y_val).group())

                # If the element has a height (like rect), add it to Y
                height_val = element.get('height')
                h_num = float(re.search(r'[\d.]+', height_val).group()) if height_val else 0.0

                # Update the maximum Y-axis value
                max_y = max(max_y, y_val + h_num)
            except (ValueError, TypeError, AttributeError):
                continue
    return max_y


def remove_footer_and_adjust_height(
    input_path: str,
    output_path: str,
    footer_id: str = 'footer',
    padding: float = 10.0
):
    # 1. Register the SVG namespace to avoid modifying/corrupting the tags
    namespace = "http://www.w3.org/2000/svg"
    ET.register_namespace('', namespace)
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

    # Parse the SVG file
    tree = ET.parse(input_path)
    root = tree.getroot()

    # 2. Find and remove the footer element
    footer_removed = False
    for parent in root.iter():
        if footer_removed:
            break

        children = list(parent)
        for index, child in enumerate(children):
            if child.get('id', '') == footer_id:
                # Found the footer!
                # Now remove the footer and ALL sibling elements that come after it
                elements_to_remove = children[index:]
                for element in elements_to_remove:
                    parent.remove(element)

                footer_removed = True
                break

    if not footer_removed:
        print(f"No <g id='{footer_id}'> found in the file.")
        return

    # 3. Calculate the new height based on the REMAINING elements
    content_max_y = 0.0

    # Search all remaining elements for attributes that define their vertical position
    for child in root.iter():
        y = get_max_y_of_element(child)
        # Update the maximum Y-axis value
        content_max_y = max(content_max_y, y)

    print(f"📐 Max y in remaining content: {content_max_y:.2f}")

    # New height = max y of content + padding
    # Alternatively, use the footer's top position directly: new_height = footer_min_y
    # Add a bottom margin (padding) to keep it visually appealing
    new_height = math.ceil(content_max_y + padding)
    print(f"📏 New height: {new_height:.2f} (padding={padding})")

    # 4. Update the viewBox and height attributes in the root <svg> tag
    old_height = root.get('height', '?')
    root.set('height', str(new_height))
    old_viewbox = root.get('viewBox', '')
    if old_viewbox:
        parts = old_viewbox.split()
        if len(parts) == 4:
            # Update the height value in the viewBox
            parts[3] = str(new_height)
            root.set('viewBox', " ".join(parts))

    print(f"🔄 height: {old_height} → {new_height:.2f}")

    # Save the new file
    tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print("Footer and all subsequent elements removed successfully!")
    print(f"The new height is: {new_height}px")
    print(f"💾 Saved to: {output_path}")


if __name__ == '__main__':
    dir_path = Path(__file__).parent / "examples/3"
    input_path = dir_path / 'Death_rate_from_smoking,_World,_2021.svg'
    output_path = dir_path / 'cropped_gemini.svg'
    remove_footer_and_adjust_height(
        input_path=input_path,
        output_path=output_path,
        footer_id='footer',
        padding=10.0,
    )
