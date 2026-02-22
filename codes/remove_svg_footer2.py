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

    def scan(el):
        nonlocal min_y
        for attr in ('y', 'y1', 'y2', 'cy'):
            val = el.get(attr)
            if val:
                try:
                    min_y = min(min_y, float(val))
                except ValueError:
                    pass
        # transform="translate(x, y)"
        transform = el.get('transform', '')
        match = re.search(r'translate\s*\(\s*[\d.+-]+\s*,\s*([\d.+-]+)', transform)
        if match:
            try:
                min_y = min(min_y, float(match.group(1)))
            except ValueError:
                pass
        for child in el:
            scan(child)

    scan(element)
    return min_y if min_y != float('inf') else None


def get_max_y_of_element(element) -> float:
    """
    Get the maximum y+height value from an SVG element and all its descendants.
    Used to calculate the actual bottom edge of the remaining content.
    """
    max_y = 0.0

    def scan(el):
        nonlocal max_y
        # y + height (for rectangles and text elements)
        y_val = None
        for attr in ('y', 'y1', 'y2', 'cy'):
            v = el.get(attr)
            if v:
                try:
                    y_val = float(v)
                    break
                except ValueError:
                    pass

        if y_val is not None:
            h_num = 0.0
            try:
                h_num = float(el.get('height', 0))
            except ValueError:
                pass
            # For text elements: use font-size as a simple height estimate
            font_size = el.get('font-size', '')
            if font_size:
                try:
                    h_num = max(h_num, float(font_size))
                except ValueError:
                    pass
            max_y = max(max_y, y_val + h_num)

        for child in el:
            scan(child)

    scan(element)
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
    footer = None
    footer_min_y = None
    children = list(root)
    footer_index = None

    for index, child in enumerate(children):
        if child.get('id', '') == footer_id:
            footer = child
            footer_min_y = get_min_y_of_element(child)
            footer_index = index
            break

    if footer is None:
        print(f"⚠️  No element found with id='{footer_id}'")
        return

    # Remove footer and every element that comes after it
    elements_to_remove = children[footer_index:]
    for el in elements_to_remove:
        el_id = el.get('id', el.tag.split('}')[-1])
        root.remove(el)
        print(f"🗑️  Removed <{el.tag.split('}')[-1]} id=\"{el_id}\">")

    print(f"✅ Total removed: {len(elements_to_remove)} element(s) (footer min y: {footer_min_y})")

    # 3. Calculate the new height based on the REMAINING elements
    content_max_y = 0.0

    # Search all remaining elements for attributes that define their vertical position
    for child in root:
        y = get_max_y_of_element(child)
        # Update the maximum Y-axis value
        content_max_y = max(content_max_y, y)

    print(f"📐 Max y in remaining content: {content_max_y:.2f}")

    # New height = max y of content + padding
    # Alternatively, use the footer's top position directly: new_height = footer_min_y
    # Add a bottom margin (padding) to keep it visually appealing
    new_height = content_max_y + padding
    print(f"📏 New height: {new_height:.2f} (padding={padding})")

    # 4. Update the viewBox and height attributes in the root <svg> tag
    old_height = root.get('height', '?')
    root.set('height', f"{new_height:.2f}")
    old_viewbox = root.get('viewBox', '')
    if old_viewbox:
        parts = old_viewbox.split()
        if len(parts) == 4:
            # Update the height value in the viewBox
            parts[3] = f"{new_height:.2f}"
            root.set('viewBox', " ".join(parts))

    print(f"🔄 height: {old_height} → {new_height:.2f}")

    # Save the new file
    tree.write(output_path, encoding='unicode', xml_declaration=False)
    # tree.write(output_path, encoding='utf-8', xml_declaration=True)
    print("Footer and all subsequent elements removed successfully!")
    print(f"The new height is: {new_height}px")
    print(f"💾 Saved to: {output_path}")


if __name__ == '__main__':
    dir_path = Path(__file__).parent / "examples/3"
    input_path = dir_path / 'Death_rate_from_smoking,_World,_2021.svg'
    output_path = dir_path / 'cropped_claude.svg'
    remove_footer_and_adjust_height(
        input_path=input_path,
        output_path=output_path,
        footer_id='footer',
        padding=10.0,
    )
