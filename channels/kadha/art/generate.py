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
 "rama": "Young Lord Rama, warm dusky brown Indian skin tone (NOT blue skin), gentle face, tall ornate golden crown with jewels, golden necklaces and armlets, yellow silk dhoti, saffron angavastram, holding a curved wooden archery bow in one hand, quiver of arrows on his back, ",
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
 "rama_child": "Little child prince Rama, about 5 years old, warm dusky brown Indian skin tone (NOT blue skin), small golden crown, yellow dhoti, gold jewellery, cute smile, ",
 "lakshmana_child": "Little child prince Lakshmana, about 5 years old, fair skin, small golden crown, orange dhoti, gold jewellery, cute smile, ",
 "bharata_child": "Little child prince Bharata, about 5 years old, wheat skin, small golden crown, green dhoti, gold jewellery, cute smile, ",
 "parashurama": "Sage Parashurama, strong warrior sage, long white beard, matted hair bun, saffron robes, rudraksha beads, holding a large axe (parashu) over his shoulder, stern but kind face, not scary, ",
 "vasishtha": "Sage Vasishtha, royal guru of Ayodhya, calm wise elderly rishi, long white beard, white hair bun with small rudraksha crown, white and saffron robes, holding a kamandalu water pot, ",
 "manthara": "Manthara, elderly palace maid, grey hair in a bun, plain brown and green cotton saree, holding a walking stick, sly scheming expression but cartoon friendly, not scary, ",
 "janaka": "King Janaka of Mithila, wise gentle middle-aged king, short black beard, golden crown, cream and gold royal robes, rudraksha beads, kind smile, ",
 "ahalya": "Ahalya, gentle graceful sage's wife, kind serene face, white and light yellow cotton saree, simple flower in hair, rudraksha bracelet, hands folded in namaste, peaceful smile, ",
 "guha": "Guha, friendly king of the boatmen tribe, dark brown skin, strong kind face, short black beard, simple headband with peacock feather, white dhoti, wooden boat oar in one hand, warm smile, ",
 "sumantra": "Sumantra, loyal elderly royal charioteer and minister, grey moustache, white turban with small jewel, cream and maroon robes, cute chibi proportions like a children's cartoon, full body head to toe visible with feet, kind sad face, ",
 "bharadwaja": "Sage Bharadwaja, kind elderly rishi, long grey beard, hair in a top bun, light orange robes, rudraksha beads, holding a wooden staff, warm welcoming smile, cute chibi proportions, full body head to toe visible with feet, ",
 "rama_forest": "Young Lord Rama during forest exile, warm dusky brown Indian skin tone (NOT blue skin), gentle face, NO crown, long black hair tied up in a hermit's top-knot bun (jata), simple tree-bark cloth garment (valkalam) in earthy brown and ochre wrapped like a dhoti with a bark-cloth upper cloth, rudraksha bead necklace, holding a curved wooden archery bow, quiver of arrows on his back, cute chibi proportions, full body head to toe visible with feet, ",
 "lakshmana_forest": "Young prince Lakshmana during forest exile, fair skin, NO crown, black hair tied up in a hermit's top-knot bun (jata), simple tree-bark cloth garment (valkalam) in earthy brown and ochre wrapped like a dhoti with a bark-cloth upper cloth, rudraksha beads, holding a curved wooden archery bow, quiver of arrows on back, alert brave face, cute chibi proportions, full body head to toe visible with feet, ",
 "sita_forest": "Goddess Sita during forest exile, young graceful, fair skin, NO crown and NO gold jewellery, long black hair in a simple braid with white jasmine and forest flowers, simple tree-bark cloth saree (valkalam) in soft earthy brown and ochre, small red bindi, holding a lotus, gentle smile, cute chibi proportions, full body head to toe visible with feet, ",
 "sutikshna": "Sage Sutikshna, kind middle-aged rishi with a short dark-grey beard, hair in a top knot, light orange robes, rudraksha beads, holding a kamandalu water pot, warm smile, full body head to toe visible with feet, ",
 "agastya": "Sage Agastya, short and sturdy wise old rishi with a long white beard and bright kind eyes, hair in a top bun, deep saffron robes, rudraksha beads, holding a kamandalu water pot, radiant calm smile, full body head to toe visible with feet, ",
 "atri": "Sage Atri, kind very old rishi, long flowing white beard, white hair in a top bun, light saffron robes, rudraksha beads, holding a wooden staff, gentle smile, full body head to toe visible with feet, ",
 "anasuya": "Anasuya Devi, kind elderly hermit mother, gentle wrinkled smiling face, white and light orange cotton saree, grey hair in a bun with flowers, rudraksha bracelet, hands together in blessing, full body head to toe visible with feet, ",
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
 "mithila_court": "grand royal court of Mithila with golden pillars and flower garlands, a single huge ornate golden archery bow lying horizontally on a long decorated golden stand in the centre of the hall, empty hall, no people, no gods, no statues, ",
 "wedding_mandapam": "a beautiful traditional Indian wedding mandapam decorated with marigold and jasmine garlands, banana trees, brass lamps glowing, sacred fire in the centre, festive colours, no people, ",
 "chariot_road": "a royal golden chariot with white horses on a road leaving an ancient Indian city gate, dusty evening light, no people, no letters, no writing, no signboards, no watermark, ",
 "ganga_bank": "the holy river Ganga at dawn, wide calm water, a small wooden boat tied at a sandy bank, tall ingudi trees, soft mist, no signature, no watermark, no letters, ",
 "panchavati": "Panchavati forest clearing beside the wide Godavari river, a small neat leaf-and-bamboo hut (parnashala) under five big banyan trees, flowering bushes, deer grazing, golden morning light, ",
 "chitrakoot": "a small leaf-and-bamboo hut beside a gentle mountain stream at Chitrakoot hill, flowering trees, peacocks, deer, soft golden sunlight, peaceful, no people, no letters, no watermark, ",
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
