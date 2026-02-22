from pathlib import Path
import re
import xml.etree.ElementTree as ET


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
            h = 0.0
            try:
                h = float(el.get('height', 0))
            except ValueError:
                pass
            # For text elements: use font-size as a simple height estimate
            font_size = el.get('font-size', '')
            if font_size:
                try:
                    h = max(h, float(font_size))
                except ValueError:
                    pass
            max_y = max(max_y, y_val + h)

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
    # Register namespaces to prevent them from being rewritten incorrectly
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')

    tree = ET.parse(input_path)
    root = tree.getroot()

    # ns = {'svg': 'http://www.w3.org/2000/svg'}
    # Support SVG files with or without a namespace prefix
    # tag_prefix = root.tag.split('}')[0] + '}' if '}' in root.tag else ''

    # Find and remove the footer element
    footer = None
    footer_min_y = None

    for child in list(root):
        child_id = child.get('id', '')
        if child_id == footer_id:
            footer = child
            footer_min_y = get_min_y_of_element(child)
            root.remove(child)
            print(f"✅ Removed <g id=\"{footer_id}\"> (footer min y: {footer_min_y})")
            break

    if footer is None:
        print(f"⚠️  No element found with id='{footer_id}'")
        return

    # Calculate the highest y in the remaining content
    content_max_y = 0.0
    for child in root:
        y = get_max_y_of_element(child)
        content_max_y = max(content_max_y, y)

    print(f"📐 Max y in remaining content: {content_max_y:.2f}")

    # New height = max y of content + padding
    # Alternatively, use the footer's top position directly: new_height = footer_min_y
    new_height = content_max_y + padding
    print(f"📏 New height: {new_height:.2f} (padding={padding})")

    # Update width, height and viewBox on the <svg> tag
    old_height = root.get('height', '?')
    root.set('height', f"{new_height:.2f}")

    view_box = root.get('viewBox', '')
    if view_box:
        parts = view_box.split()
        if len(parts) == 4:
            parts[3] = f"{new_height:.2f}"
            root.set('viewBox', ' '.join(parts))

    print(f"🔄 height: {old_height} → {new_height:.2f}")

    tree.write(output_path, encoding='unicode', xml_declaration=False)
    print(f"💾 Saved to: {output_path}")


if __name__ == '__main__':
    dir_path = Path(__file__).parent / "examples/1"
    input_path = dir_path / 'Daily_meat_consumption_per_person,_World,_2022.svg'
    output_path = dir_path / 'cropped_claude.svg'
    remove_footer_and_adjust_height(
        input_path=input_path,
        output_path=output_path,
        footer_id='footer',
        padding=10.0,
    )
