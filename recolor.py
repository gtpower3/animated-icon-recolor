import json
from pathlib import Path
from rlottie_python import LottieAnimation

icons_dir = Path("./icons")
output_dir = Path("./output")
output_dir.mkdir(exist_ok=True)

DEFAULT_BASE = "#1A1833"
DEFAULT_HIGHLIGHT = "#0550F0"

def hex_to_lottie(hex_color):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
    return [r, g, b, 1.0]

def prompt_hex(prompt, default):
    while True:
        value = input(f"{prompt} (hex) [{default}]: ").strip()
        if value == "":
            return default
        value = value if value.startswith("#") else f"#{value}"
        if len(value) == 7:
            try:
                int(value[1:], 16)
                return value
            except ValueError:
                pass
        print(f"  Invalid hex color, please try again (e.g. #FF0000 or FF0000)")

base_hex = prompt_hex("Base color", DEFAULT_BASE)
highlight_hex = prompt_hex("Highlight color", DEFAULT_HIGHLIGHT)
base_color = hex_to_lottie(base_hex)
highlight_color = hex_to_lottie(highlight_hex)

def recolor_strokes(obj, base_color, highlight_color):
    if isinstance(obj, dict):
        if "k" in obj and isinstance(obj["k"], list) and len(obj["k"]) in (3, 4):
            k = obj["k"]
            if all(isinstance(v, (int, float)) for v in k):
                if len(k) >= 3 and abs(k[0]) < 0.01 and abs(k[1]) < 0.01 and abs(k[2]) < 0.01:
                    obj["k"] = base_color
                elif len(k) >= 3 and k[1] > 0.7 and k[2] > 0.7 and k[0] < 0.4:
                    obj["k"] = highlight_color
        for v in obj.values():
            recolor_strokes(v, base_color, highlight_color)
    elif isinstance(obj, list):
        for item in obj:
            recolor_strokes(item, base_color, highlight_color)

for json_file in icons_dir.glob("*.json"):
    print(f"Processing {json_file.name}...")

    with open(json_file) as f:
        data = json.load(f)

    recolor_strokes(data, base_color, highlight_color)

    recolored_path = output_dir / json_file.with_suffix(".recolored.json").name
    with open(recolored_path, "w") as f:
        json.dump(data, f)

    gif_path = output_dir / json_file.with_suffix(".gif").name
    anim = LottieAnimation.from_file(str(recolored_path))
    anim.save_animation(str(gif_path), fps=25)

    print(f"  Saved {gif_path.name}")

print(f"Done! Saved to the \"{output_dir}\" folder")