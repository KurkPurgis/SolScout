import sys
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB"); W, H = im.size
big = im.resize((W*2, H*2), Image.NEAREST); W, H = big.size
d = ImageDraw.Draw(big)
d.rectangle([W*0.08, H*0.08, W*0.92, H*0.92], outline=(255, 40, 200), width=2)
small = Image.open(sys.argv[3]).convert("RGB")
sheet = Image.new("RGB", (W + 20 + small.width, H), (30, 30, 30))
sheet.paste(big, (0, 0)); sheet.paste(small, (W + 10, (H - small.height)//2))
sheet.save(out)
