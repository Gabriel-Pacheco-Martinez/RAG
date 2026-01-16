from typing import Dict

def get_fonts(fonts: Dict[str, int]):
    # Most repeated font by count (Chunk font)
    most_repeated_font = max(fonts, key=fonts.get)
    
    # Get font sizes
    sorted_fonts = sorted(map(int, fonts.keys()), reverse=True)
    return {
        "title": sorted_fonts[0] if len(sorted_fonts) > 0 else None,
        "chapter": sorted_fonts[1] if len(sorted_fonts) > 1 else None,
        "section": sorted_fonts[2] if len(sorted_fonts) > 2 else None,
        "chunk": int(most_repeated_font)
    }