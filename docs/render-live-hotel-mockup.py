"""Render the original design boards; documentation only, no live data or APIs.

Run with an existing Pillow environment. Refuses to overwrite the v1 originals.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
BG, INK, MUTED = '#F5F3EE', '#17332D', '#53645F'
LINE, GREEN, SOFT, WHITE = '#CCD4CE', '#245C4E', '#E8F0EA', '#FFFFFF'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'


def board(h):
    im = Image.new('RGB', (1800, h), BG)
    return im, ImageDraw.Draw(im)


def text(d, xy, value, size=22, color=INK, bold=False):
    d.text(xy, value, font=ImageFont.truetype(BOLD if bold else FONT, size), fill=color)


def lines(d, x, y, values, size=22, color=MUTED, step=29):
    for n, value in enumerate(values):
        text(d, (x, y + n * step), value, size, color)


def box(d, coords, fill=WHITE, outline=LINE, radius=12, width=2):
    d.rounded_rectangle(coords, radius, fill=fill, outline=outline, width=width)


def button(d, x, y, label, w=128, fill=GREEN):
    box(d, (x, y, x+w, y+48), fill, fill, 8)
    text(d, (x+18, y+12), label, 22, WHITE, True)


def marker(d, x, y, label, selected=False):
    if selected:
        d.ellipse((x-26, y-26, x+26, y+26), outline=INK, width=3)
    d.ellipse((x-19, y-19, x+19, y+19), fill=GREEN if selected else WHITE, outline=GREEN, width=2)
    text(d, (x-7, y-13), label, 22, WHITE if selected else INK, True)


def map_sketch(d, x, y, w, h):
    box(d, (x, y, x+w, y+h), '#EDF1EA')
    text(d, (x+18, y+14), 'Leaflet map · schematic', 21, INK, True)
    text(d, (x+18, y+43), 'No real tiles or hotel positions', 17, MUTED)
    cx, cy, r = x+w*.48, y+h*.53, min(w*.30, h*.30)
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill='#DFE9DD', outline='#7B9A85', width=2)
    d.line((cx, cy, cx+r, cy), fill='#7B9A85', width=2)
    text(d, (cx+22, cy+9), '5 km', 18)
    d.rectangle((cx-6, cy-6, cx+6, cy+6), fill=INK)
    text(d, (cx-72, cy+40), 'ZIP center', 18, INK, True)
    marker(d, cx-57, cy-63, '1', True)
    marker(d, cx+78, cy-53, '2')
    marker(d, cx-75, cy+25, '3')
    box(d, (x+16, y+h-91, x+w-16, y+h-57), WHITE)
    text(d, (x+28, y+h-85), '1  Selected · same list item', 18, INK, True)
    text(d, (x+16, y+h-46), 'Leaflet | © OpenStreetMap contributors', 16)
    text(d, (x+16, y+h-25), 'Powered by Geoapify', 16)


def row(d, x, y, w, number, name, detail, selected=False):
    box(d, (x, y, x+w, y+91), SOFT if selected else WHITE, GREEN if selected else LINE)
    if selected:
        box(d, (x-5, y-5, x+w+5, y+96), None, '#996326', 14, 2)
    text(d, (x+16, y+14), f'{number}  {name}', 22, INK, True)
    text(d, (x+16, y+45), detail, 19, MUTED)
    if selected:
        text(d, (x+16, y+68), 'Selected · keyboard focus', 16, GREEN)


layout, d = board(1390)
text(d, (50, 38), 'WAYFINDER / LIVE HOTEL DISCOVERY', 21, GREEN, True)
text(d, (50, 77), 'Early mockup: one search, two connected views', 43, INK, True)
text(d, (50, 135), 'Original v1 · 29 Sep 2026 · Before implementation · All hotel entries are labeled placeholders', 22, MUTED)
text(d, (50, 196), '01  DESKTOP / LIST + MAP', 23, GREEN, True)
text(d, (1250, 196), '02  NARROW / STACKED', 23, GREEN, True)

box(d, (50, 237, 1195, 1050))
text(d, (80, 265), 'Wayfinder', 29, INK, True)
text(d, (305, 273), 'Discover hotels', 21, GREEN, True)
text(d, (925, 273), 'Sample stays & bookings', 19, MUTED)
d.line((80, 316, 1165, 316), fill=LINE, width=2)
text(d, (80, 341), 'Find hotels near a U.S. ZIP', 32, INK, True)
text(d, (80, 392), 'U.S. ZIP code', 20, INK, True)
box(d, (80, 421, 300, 473))
text(d, (96, 434), '02108', 24)
button(d, 317, 423, 'Search')
text(d, (465, 436), 'Five digits; keep leading zeros.', 20, MUTED)
text(d, (80, 499), 'Returned ZIP center: 02108 · Boston, US', 23, INK, True)
text(d, (80, 533), 'Within 5 km of Geoapify’s returned postcode point.', 21, MUTED)
text(d, (80, 574), '3 example rows shown · Search returns up to 20 hotels.', 20, INK, True)
text(d, (80, 604), 'Coverage varies. Results are not a complete hotel inventory.', 19, MUTED)
row(d, 80, 651, 442, '1', '[Provider hotel name]', '[Provider address]', True)
row(d, 80, 758, 442, '2', 'Name not provided', '[Provider address]')
row(d, 80, 865, 442, '3', '[Provider hotel name]', 'Address not provided')
text(d, (80, 985), 'Hotel information only · no booking service', 19, MUTED)
map_sketch(d, 554, 650, 610, 375)

box(d, (1250, 237, 1750, 1205), WHITE, LINE, 22)
text(d, (1274, 266), 'Wayfinder', 28, INK, True)
text(d, (1274, 308), 'Discover hotels', 24, GREEN, True)
text(d, (1274, 345), 'Sample stays & bookings →', 18, MUTED)
d.line((1274, 380, 1726, 380), fill=LINE, width=2)
text(d, (1274, 400), 'U.S. ZIP code', 20, INK, True)
box(d, (1274, 431, 1536, 481))
text(d, (1290, 444), '02108', 23)
button(d, 1551, 432, 'Search', 175)
text(d, (1274, 498), 'Five digits, including leading zeros.', 19, MUTED)
lines(d, 1274, 537, ['Returned ZIP center: 02108', 'Boston, US · 5 km radius'], 22, INK)
lines(d, 1274, 605, ['Up to 20 hotels. Coverage varies.', 'Not a complete inventory.'], 19)
map_sketch(d, 1274, 667, 452, 323)
row(d, 1274, 1010, 452, '1', '[Provider hotel name]', '[Provider address]', True)
text(d, (1274, 1122), '2  Name not provided', 21, INK, True)
text(d, (1274, 1155), 'More results continue down the page ↓', 18, MUTED)

text(d, (50, 1090), 'A  Selection works both ways', 24, INK, True)
lines(d, 50, 1128, ['Select a row → reveal its marker. Select a marker → reveal its row.',
                      'Use provider ID, not hotel name, to keep the same place selected.'], 22)
text(d, (50, 1210), 'B  A postcode point, not your location', 24, INK, True)
lines(d, 50, 1248, ['The circle is 5,000 meters around Geoapify’s returned ZIP point.',
                      'It does not cover every address in the ZIP area or follow the traveler.'], 22)
lines(d, 1250, 1248, ['C  One page scroll; no tiny split panes.',
                       'Marker selection reveals its list row.',
                       'Attribution stays visible.'], 21)
text(d, (50, 1350), 'Keyboard: Tab to controls and hotels; Enter/Space selects a list button; Enter activates a marker. Focus is outlined.', 21, INK)

states, d = board(1140)
text(d, (50, 38), 'WAYFINDER / INTERACTION STATES', 21, GREEN, True)
text(d, (50, 77), 'Every outcome has its own message', 43, INK, True)
text(d, (50, 135), 'Original v1 · Annotated state sketches · Example text, not captured provider responses', 22, MUTED)

items = [
 ('01  INITIAL', ['U.S. ZIP code   [ e.g. 02108 ]  [ Search ]', 'Enter five digits to discover nearby hotels.'], ['No request until Search or Enter.', 'Show radius explanation; no old results.']),
 ('02  LOADING', ['[ 02108 ]  [ Searching… disabled ]', 'Finding hotels near ZIP 02108…'], ['Announce progress; prevent repeat submit.', 'Clear stale rows, markers and selection.']),
 ('03  RESULTS', ['[ N ] hotels returned · Up to 20 shown.', 'Select a hotel in the list or on the map.'], ['At cap: “Additional places may exist.”', 'Do not promise exhaustive coverage.']),
 ('04  INVALID INPUT', ['[ 2108 ]  [ Search ]', 'Enter a five-digit U.S. ZIP code.'], ['Inline error is associated with the field.', 'Keep input; do not contact provider.']),
 ('05  UNRESOLVED ZIP', ['We could not locate that U.S. ZIP.', 'Check the five digits or try another ZIP.'], ['No nearby-hotel request or fallback city.', 'This is different from no hotels returned.']),
 ('06  NO NEARBY HOTELS', ['No hotels were returned within 5 km', 'of the returned ZIP center.'], ['Keep the center and radius; no hotel pins.', 'Do not say “There are no hotels here.”']),
 ('07  FAILED REQUEST', ['We could not complete this search.', '[ Retry ]  Your ZIP stays in the field.'], ['Show a service error, not an empty list.', 'Respect retry delay; no retry loop.']),
 ('08  MAP IMAGERY FAILURE', ['Map imagery is unavailable.', 'Hotel information is still shown below.'], ['Keep successful hotel results accessible.', 'Do not label this a failed hotel search.']),
]
for n, (title, copy, notes) in enumerate(items):
    x, y = 50+(n%2)*875, 204+(n//2)*199
    box(d, (x, y, x+825, y+178))
    text(d, (x+20, y+16), title, 20, GREEN, True)
    lines(d, x+20, y+49, copy, 22, INK, 29)
    lines(d, x+20, y+115, notes, 18, MUTED, 25)
text(d, (50, 1030), 'Missing fields: “Name not provided” / “Address not provided”. Never fabricate names, locations or prices.', 22, INK, True)
text(d, (50, 1075), 'Sample stays & bookings remain a separate labeled destination. Live discovery has no ratings, availability or booking actions.', 21, MUTED)

for name, image in [('live-hotel-mockup-v1.png', layout), ('live-hotel-states-v1.png', states)]:
    path = ROOT / name
    if path.exists():
        raise SystemExit(f'Refusing to overwrite original: {path}')
    image.save(path)
    print(path)
