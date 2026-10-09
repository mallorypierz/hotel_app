"""Documentation-only original boards. Existing Pillow runtime; no app imports.

Refuses to overwrite v1. Later revisions must use new filenames.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ['chatbot-desktop-v1.png', 'chatbot-mobile-v1.png', 'chatbot-states-v1.png']
if any((ROOT / name).exists() for name in OUT):
    raise SystemExit('Original v1 exists; preserve it and create a new version.')
BG, INK, MUTED, GREEN = '#F6F3EC', '#17332D', '#50625D', '#245B50'
LINE, SOFT, AMBER = '#C6D2CB', '#E4EEE8', '#8A521E'
LABEL = 'Simulated course rates and availability—not real booking information'
QUESTION = 'Which saved hotels in 06109 have one room from Oct 10 to Oct 12, 2026, for $350 total or less?'
MODEL = 'OpenAI · gpt-4.1-mini-2025-04-14'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
SERIF = '/System/Library/Fonts/Supplemental/Georgia.ttf'
MONO = '/System/Library/Fonts/Menlo.ttc'

class Board:
    def __init__(self,w,h,scale=1):
        self.w,self.h,self.scale=w,h,scale
        self.im=Image.new('RGB',(w*scale,h*scale),BG)
        self.d=ImageDraw.Draw(self.im)
    def box(self,x,y,w,h,fill='white',outline=LINE,r=12,width=1):
        s=self.scale
        self.d.rounded_rectangle((x*s,y*s,(x+w)*s,(y+h)*s),r*s,fill,outline,width=width*s)
    def text(self,x,y,t,size=18,color=INK,bold=False,width=None,serif=False,mono=False,gap=1.35):
        f=ImageFont.truetype(MONO if mono else SERIF if serif else BOLD if bold else FONT,size*self.scale)
        rows=[]
        for line in t.split('\n'):
            if width is None:
                rows.append(line); continue
            row=''
            for word in line.split(' '):
                test=(row+' '+word).strip()
                if self.d.textlength(test,font=f)>width*self.scale and row:
                    rows.append(row);row=word
                else:row=test
            rows.append(row)
        for i,line in enumerate(rows):
            assert x*self.scale+self.d.textlength(line,font=f) <= self.im.width-8, line
            self.d.text((x*self.scale,(y+i*size*gap)*self.scale),line,font=f,fill=color)
        return y+len(rows)*size*gap
    def button(self,x,y,t,w=120,disabled=False):
        self.box(x,y,w,46,'#E0E5E1' if disabled else GREEN)
        self.text(x+16,y+12,t,16,MUTED if disabled else 'white',True)
    def save(self,name):
        self.im.save(ROOT/name)

b=Board(1440,1660)
b.text(48,25,'EARLY DESIGN / ORIGINAL V1 / 08 OCT 2026',16,GREEN,True)
b.text(48,55,'Desktop · saved-hotel assistant',34,serif=True)
b.text(48,104,'Illustrative UI only. Fictional hotel records, SQL and answers; no API call or database query was made.',18,MUTED)
b.box(40,151,1360,1415)
b.text(72,176,'Wayfinder',28,serif=True)
b.text(405,186,'Discover hotels     Ask saved hotels     Sample stays & bookings     Booking history',18,MUTED)
b.box(72,230,1296,88,BG)
b.text(92,245,'Existing discovery stays above this section',18,bold=True)
b.text(92,276,'ZIP search · synchronized list/map · Add/Remove from Local · visible map attribution',17,MUTED)
b.text(80,348,'SAVED HOTEL ASSISTANT',15,AMBER,True)
b.text(80,378,'Find a stay in your saved hotels.',36,serif=True)
b.text(80,431,'Compare dates, simulated costs and room counts. Results cover saved hotels only.',19,MUTED)
b.box(80,473,1280,52,SOFT)
b.text(98,489,LABEL,19,GREEN,True)
b.text(80,553,'Your question',19,bold=True)
b.box(78,580,1103,90,'white',AMBER,width=3)
b.text(96,598,QUESTION,20,width=1060)
b.button(1200,598,'Send',140)
b.text(80,685,'Tab to Send, then Enter or Space. Enter in the question field starts a new line.',16,MUTED)
b.text(80,711,'Your question and relevant saved records are sent to OpenAI. Please omit personal information.',16,MUTED)
b.text(80,757,'2 matches in this illustrative example',24,bold=True)
b.text(80,795,'Oct 10–12, 2026 · 2 nights · 1 room · checkout night excluded',18,MUTED)
for x,name,cost,rooms,reason in [(80,'Example Birch House','$260','At least 2 rooms each night','Lowest total at $260. Both nights have a room.'),(730,'Example River Inn','$300','At least 5 rooms each night','Alternative with more rooms. Both nights covered.')]:
    b.box(x,833,630,175,SOFT if x==80 else 'white')
    b.text(x+20,850,name,24,bold=True)
    b.text(x+20,891,cost+' total / 1 room',27,serif=True)
    b.text(x+20,932,rooms,18,bold=True)
    b.text(x+20,965,reason,17,width=586)
b.text(80,1025,'Recommendation: Example Birch House meets your dates and budget at the lower simulated total.',18,width=1240)
b.box(80,1074,1280,414,BG)
b.text(100,1091,'− How this answer was produced',22,bold=True)
b.text(100,1125,'Read-only evidence · expanded for this mockup · Enter/Space toggles the disclosure',15,MUTED)
b.text(100,1160,'Original question',16,bold=True)
b.text(100,1185,QUESTION,16,width=1240)
b.text(100,1221,'Proposed SQL · illustrative SELECT',16,bold=True)
sql="SELECT h.hotel_id, h.name, COUNT(*) AS nights, SUM(n.nightly_rate_cents) AS total_cents,\n       MIN(n.rooms_available) AS min_rooms FROM saved_hotels h\nJOIN demo_hotel_nights n USING(hotel_id) WHERE n.stay_date >= ? AND n.stay_date < ?\nAND EXISTS (SELECT 1 FROM saved_hotel_locations l WHERE l.hotel_id=h.hotel_id AND l.postcode=?)\nGROUP BY h.hotel_id, h.name HAVING COUNT(*)=? AND MIN(n.rooms_available)>=?\nAND SUM(n.nightly_rate_cents)<=? ORDER BY total_cents, h.hotel_id LIMIT 20"
b.text(100,1249,sql,15,mono=True)
b.text(100,1379,'Parameters: [2026-10-10, 2026-10-12, 06109, 2, 1, 35000] · dates and ZIP are strings',15,MUTED)
b.text(100,1404,'Validation: allowed read-only SELECT · 2 rows / limit 20 · no truncation (illustrative)',16,GREEN,True)
b.text(100,1430,'Records: demo-birch | Example Birch House | 2 | 26000 | 2; demo-river | Example River Inn | 2 | 30000 | 5',14,mono=True)
b.text(100,1462,MODEL+' · used for both proposed model calls',16,MUTED)
b.text(80,1514,'Existing Sample stays & bookings continues below. The assistant has no booking action.',18,MUTED)
b.text(48,1590,'DESIGN NOTES  •  Full-page scroll  •  Visible focus ring  •  Evidence collapsed by default  •  No editable SQL',17,GREEN)
b.save(OUT[0])

m=Board(390,1760,2)
m.text(20,18,'ORIGINAL V1 · MOBILE · 390 PX',12,GREEN,True)
m.text(20,42,'Illustrative content only',16,bold=True)
m.text(20,73,'Wayfinder',26,serif=True)
m.text(20,113,'Discover hotels   ·   Ask saved hotels',14,GREEN)
m.text(20,139,'Sample stays & bookings   ·   History',14,MUTED)
m.box(16,177,358,65,'white')
m.text(28,190,'Existing discovery above',16,bold=True)
m.text(28,216,'ZIP / list / map / local save controls',14,MUTED)
m.text(20,270,'SAVED HOTEL ASSISTANT',12,AMBER,True)
m.text(20,299,'Ask your saved hotels.',29,serif=True)
m.text(20,345,'Compare saved stays for your dates.',16,MUTED)
m.box(16,380,358,82,SOFT)
m.text(28,396,LABEL,16,GREEN,True,width=326)
m.text(20,490,'Your question',17,bold=True)
m.box(16,521,358,126,'white',AMBER,width=2)
m.text(28,534,QUESTION,17,width=326)
m.button(16,663,'Send',358)
m.text(20,723,'Tab → Send; Enter/Space submits.\nEnter in the field adds a new line.',14,MUTED,width=350)
m.text(20,774,'Question + relevant saved records go to OpenAI. Omit personal information.',14,MUTED,width=350)
m.text(20,834,'2 illustrative matches',23,bold=True)
m.text(20,873,'Oct 10–12, 2026 · 2 nights · 1 room\nCheckout excluded. Saved hotels only.',15,MUTED)
m.box(16,933,358,195,SOFT)
m.text(30,951,'Example Birch House',22,bold=True)
m.text(30,989,'$260 total / 1 room',28,serif=True)
m.text(30,1035,'At least 2 rooms on each night',16,bold=True)
m.text(30,1065,'Recommended: lower total, with a room on both nights.',16,width=322)
m.box(16,1144,358,180,'white')
m.text(30,1162,'Example River Inn',22,bold=True)
m.text(30,1200,'$300 total / 1 room',28,serif=True)
m.text(30,1245,'At least 5 rooms on each night',16,bold=True)
m.text(30,1275,'Alternative with more rooms.',16,width=320)
m.box(16,1343,358,77,BG)
m.text(28,1357,'+ How this answer was produced',16,bold=True)
m.text(28,1387,'Read-only evidence · tap or Enter/Space',13,MUTED)
m.text(20,1442,'When expanded: question, SQL, validation, records and OpenAI model. SQL wraps; record fields stack.',15,MUTED,width=346)
m.box(16,1525,358,88,'white')
m.text(28,1540,'Sample stays & bookings',20,serif=True)
m.text(28,1575,'Existing separate workflow below',14,MUTED)
m.text(20,1635,'DESIGN TARGET: 320–390 px reflow;\n44 px controls; 16+ px primary text.\nStatic sketch, not a browser test.',14,GREEN,width=350)
m.save(OUT[1])

s=Board(1440,1410)
s.text(48,28,'ORIGINAL V1 / FEEDBACK STATES',17,GREEN,True)
s.text(48,65,'One question. Clear feedback at every step.',34,serif=True)
s.text(48,116,'All cards are illustrative alternatives, not observed requests or generated answers. 08 Oct 2026.',18,MUTED)
states=[
 ('01 / READY','Ask about saved hotels','Include a ZIP, check-in, checkout and room count. Specify a nightly or total budget.','Your question: [empty field]','Send (disabled until nonblank)','Example prompts fill the field; they do not submit.'),
 ('02 / LOADING','Preparing your answer…','Keep the submitted question visible. Announce progress politely; do not display an old answer as current.','Question retained · panel marked busy','Sending… (disabled)','No invented stage progress; announce only known stages.'),
 ('03 / NO MATCHES','No saved hotels match this budget','Example: Oct 10–12 in 06109, one room, $200 total maximum. No complete eligible stay matched.','Try another budget, dates or ZIP.','Edit question','Evidence: allowed SELECT, zero eligible rows. Not an outage.'),
 ('04 / INSUFFICIENT DATA','A night is missing from the saved data','Example: Oct 14–16. No record for Oct 15. We cannot confirm the full stay or its total cost.','Missing nights are never treated as available.','Edit dates','Evidence identifies the retrieved data and the missing date.'),
 ('05 / REQUEST FAILURE','We couldn’t complete your answer','The model request timed out. Your question is still here. Retry when ready; no answer was produced.','No stale answer or invented fallback.','Retry question','For rate limits, show the wait; for setup errors, show guidance.'),
 ('06 / CLARIFICATION','Which dates should I compare?','Example: “Find something affordable in 06109.” Ask for check-in, checkout and what affordable means.','Update your question to include the details.','Edit question','No database query until enough information is supplied.')]
for i,(tag,title,body,helper,action,note) in enumerate(states):
    x=48+(i%2)*688;y=180+(i//2)*390
    s.box(x,y,656,366)
    s.text(x+20,y+17,tag,14,GREEN,True)
    s.box(x+18,y+48,620,57,SOFT)
    s.text(x+30,y+60,LABEL,16,GREEN,True,width=590)
    s.text(x+20,y+123,title,23,bold=True,width=612)
    s.text(x+20,y+165,body,18,width=610)
    s.text(x+20,y+245,helper,16,MUTED,width=610)
    s.button(x+20,y+278,action,275,'disabled' in action)
    s.text(x+20,y+336,note,13,MUTED,width=613)
s.text(48,1364,'Answer state and expanded evidence appear on the desktop board; mobile uses the same state copy.',17,GREEN)
s.save(OUT[2])
print('Created:', ', '.join(OUT))
