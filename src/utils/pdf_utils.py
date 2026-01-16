from collections import defaultdict

def extract_blocks_from_page(page, file_name):
    """
    Extract text blocks with layout and font info from a single page.
    Returns a tuple: (list of blocks, font_sizes dict for this page).
    Each block is a line of text on the document.
    """
    lines = []
    font_sizes = defaultdict(int)  # counts font sizes on this page
    page_dict = page.get_text("dict")

    for block in page_dict["blocks"]:
        if block["type"] != 0: # This means it will only look for text type blocks
            continue

        for line in block["lines"]:
            text = ""
            span_sizes = []
            fonts = []
            y0s = []
            y1s = []

            for span in line["spans"]:
                text += span["text"].strip() + " "
                span_sizes.append(span["size"])
                fonts.append(span["font"])
                y0s.append(span["bbox"][1])
                y1s.append(span["bbox"][3])

            max_size = max(span_sizes)
            font_sizes[max_size] += 1  # count font size occurrence

            lines.append({
                "text": text.strip(),
                "font_size": max_size,
                "font": fonts[0],
                "bold": "Bold" in fonts[0],
                "y0": min(y0s),
                "y1": max(y1s),
                "page": page.number,
                "file": file_name
            })

    return lines, font_sizes