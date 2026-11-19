#!/usr/bin/env python3
"""Generate Kadhapetti Ramayanam art with Cloudflare Workers AI (FLUX.1-schnell, Apache-2.0).
Token is injected by the network proxy for api.cloudflare.com. Usage: python3 generate.py [name ...]"""
import base64, json, os, sys, urllib.request
from PIL import Image, ImageDraw
ACCOUNT = "d93a3d51bd1c05e669119b7955ac7aba"
HERE = os.path.dirname(os.path.abspath(__file__))
STYLE = ("for a children's devotional storybook, cute soft painted digital illustration, warm traditional Indian devotional art style, "
         "clean outlines, kind gentle expression, standing full body front view, plain pure white background, no text, no frame")
BGSTYLE = "children's storybook background painting, soft painted digital illustration, warm colours, no people, no text"
CHARS = {
 "rama": "Young Lord Rama, blue skin, tall ornate golden crown with jewels, golden necklaces and armlets, yellow silk dhoti, saffron angavastram, holding a curved wooden archery bow in one hand, quiver of arrows on his back, ",
 "sita": "Goddess Sita, young graceful princess, fair skin, red silk saree with golden border, small golden crown, jasmine flowers in hair, gold jewellery, holding a lotus, ",
 "lakshmana": "Young prince Lakshmana, fair skin, golden crown, golden jewellery, orange silk dhoti, red angavastram, holding a curved wooden archery bow, quiver of arrows on back, ",
 "bharata": "Young prince Bharata, wheat brown skin, golden crown, golden jewellery, green silk dhoti, yellow angavastram, hands folded in namaste, ",
 "shatrughna": "Young prince Shatrughna, fair skin, golden crown, golden jewellery, purple silk dhoti, yellow angavastram, holding a small sword, ",
 "hanuman": "Lord Hanuman, friendly devotional vanara, reddish orange fur face, golden crown, golden jewellery, red dhoti, holding a golden mace gada on his shoulder, other hand raised in blessing, ",
 "dasharatha": "King Dasharatha of Ayodhya, elderly kind king, white beard and moustache, tall golden crown, royal maroon and gold robes, white dhoti, gold jewellery, ",
 "kausalya": "Queen Kausalya, kind elderly-young queen, fair skin, yellow silk saree with red border, golden crown, gold jewellery, ",
 "kaikeyi": "Queen Kaikeyi, beautiful queen, wheat skin, purple silk saree with golden border, golden crown, gold jewellery, ",
 "sumitra": "Queen Sumitra, gentle queen, fair skin, green silk saree with golden border, golden crown, gold jewellery, ",
 "vishwamitra": "Sage Vishwamitra, wise elderly rishi, long white beard, white hair tied in a bun, saffron robes, rudraksha beads, holding a wooden staff, ",
 "ravana": "King Ravana of Lanka for kids, ten heads in a row each with a golden crown, dark skin, grand red and black royal robes, gold jewellery, proud but not scary, ",
 "vibhishana": "Vibhishana, kind noble demon prince, dark skin, golden crown, white and gold royal robes, hands folded in namaste, ",
 "jatayu": "Jatayu the brave giant eagle, golden brown feathers, wise kind eyes, wings spread, ",
 "rama_child": "Little child prince Rama, about 5 years old, blue skin, small golden crown, yellow dhoti, gold jewellery, cute smile, ",
 "lakshmana_child": "Little child prince Lakshmana, about 5 years old, fair skin, small golden crown, orange dhoti, gold jewellery, cute smile, ",
 "bharata_child": "Little child prince Bharata, about 5 years old, wheat skin, small golden crown, green dhoti, gold jewellery, cute smile, ",
 "ahalya": "Ahalya, gentle graceful sage's wife, kind serene face, white and light yellow cotton saree, simple flower in hair, rudraksha bracelet, hands folded in namaste, peaceful smile, ",
 "shatrughna_child": "Little child prince Shatrughna, about 5 years old, fair skin, small golden crown, purple dhoti, gold jewellery, cute smile, ",
}
BGS = {
 "ayodhya": "the golden city of Ayodhya with a grand ancient Indian palace, temple towers, flags, river Sarayu in front, sunny blue sky, ",
 "palace_hall": "inside a grand ancient Indian royal palace hall, golden pillars, red carpets, lamps, throne, ",
 "forest": "peaceful green Indian forest with tall trees, flowers, deer in distance, sunlight, ",
 "ashram": "a sage's hermitage in the forest, small huts with thatched roofs, sacred fire altar, trees, calm morning, ",
 "river": "calm wide Indian river with a small wooden boat on the bank, palm trees, sunset sky, ",
 "ocean": "vast blue ocean seen from a rocky Indian seashore, waves, sunrise, ",
 "lanka": "golden city of Lanka on a hill across the sea, golden towers and palaces, evening sky, ",
 "ahalya_ashram": "a quiet old empty hermitage in the forest, small hut with thatched roof, a large smooth grey stone shaped like a seated person in the courtyard, soft morning light, falling leaves, ",
 "night_forest": "forest at night under a full moon and stars, fireflies, peaceful, ",
}

def gen(prompt):
    req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT}/ai/run/@cf/black-forest-labs/flux-1-schnell",
        data=json.dumps({"prompt": prompt, "steps": 8}).encode(), headers={"Content-Type": "application/json", "Authorization": "Bearer proxy-injected"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return base64.b64decode(json.load(r)["result"]["image"])

def cutout(src, dst):
    im = Image.open(src).convert("RGB"); w, h = im.size
    key = (255, 0, 255)
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (0, h // 2), (w - 1, h // 2)]:
        if sum(im.getpixel((x, y))) > 690:
            ImageDraw.floodfill(im, (x, y), key, thresh=40)
    rgba = im.convert("RGBA"); px = rgba.load()
    for yy in range(h):
        for xx in range(w):
            if px[xx, yy][:3] == key: px[xx, yy] = (0, 0, 0, 0)
    bb = rgba.getbbox(); rgba.crop(bb).save(dst)

if __name__ == "__main__":
    names = sys.argv[1:] or list(CHARS) + list(BGS)
    for n in names:
        if n in CHARS:
            raw = os.path.join(HERE, "raw", n + ".jpg")
            open(raw, "wb").write(gen(CHARS[n] + STYLE)); cutout(raw, os.path.join(HERE, "chars", n + ".png"))
        else:
            open(os.path.join(HERE, "bg", n + ".jpg"), "wb").write(gen(BGS[n] + BGSTYLE))
        print("done", n, flush=True)
