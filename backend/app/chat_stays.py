"""Independent stay-intent checks and deterministic facts from local nightly records."""
from datetime import date, timedelta
from decimal import Decimal
import json
import re
from .chat_contracts import StayIntent
from .chat_queries import RetrievalError

CANONICAL_SQL = '''SELECT h.hotel_id, h.name, n.stay_date, n.nightly_rate_cents, n.rooms_available
FROM saved_hotels h LEFT JOIN demo_hotel_nights n ON n.hotel_id=h.hotel_id
AND n.stay_date>=? AND n.stay_date<?
WHERE EXISTS (SELECT 1 FROM saved_hotel_locations l WHERE l.hotel_id=h.hotel_id AND l.postcode=?)
ORDER BY h.hotel_id, n.stay_date'''
COLUMNS = ['hotel_id', 'name', 'stay_date', 'nightly_rate_cents', 'rooms_available']
MONTHS = {m: i for i, m in enumerate(('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'), 1)}
WORDS = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
CLARIFICATION = ('Please specify one five-digit ZIP, check-in and checkout dates with a year '
                 '(for example 2026-10-10 to 2026-10-12), 1–10 rooms, and whether any dollar budget '
                 'is for the total stay or per night per room. Stays may be 1–14 nights.')


def explicit_intent(question):
    """Conservative v1 grammar: never infer a date/year or silently assume rooms.

    The LLM may understand broader phrasing, but ambiguous/unsupported text asks
    for clarification before SQL. Compare these independently read facts to it.
    """
    q = question.lower()
    # Expand only a range with an explicitly shared month and year.
    month_pattern = (r'jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|'
                     r'jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?')
    shared_range = (rf'\b(?P<month>{month_pattern})\s+(?P<start>\d{{1,2}})(?:st|nd|rd|th)?'
                    r'\s*(?:to|through|[–—-])\s*(?P<end>\d{1,2})(?:st|nd|rd|th)?'
                    r',?\s+(?P<year>20\d{2})\b')
    q = re.sub(shared_range, lambda m: f"{m['month']} {m['start']} {m['year']} to "
               f"{m['month']} {m['end']} {m['year']}", q)
    zips = set(re.findall(r'(?<!\d)[0-9]{5}(?!\d)', q))
    rooms = [WORDS.get(v, int(v) if v.isdigit() else 0)
             for v in re.findall(r'\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\s+rooms?\b', q)]
    dates = []
    years = set(re.findall(r'\b(20\d{2})\b', q))
    pattern = (r'\b(?P<iso>\d{4}-\d{2}-\d{2})\b|\b(?P<month>jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|'
               r'apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|'
               r'nov(?:ember)?|dec(?:ember)?)\s+(?P<day>\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(?P<year>20\d{2}))?\b')
    try:
        for match in re.finditer(pattern, q):
            if match['iso']:
                dates.append(date.fromisoformat(match['iso']))
            else:
                year = match['year'] or (next(iter(years)) if len(years) == 1 else None)
                if not year:
                    return None
                dates.append(date(int(year), MONTHS[match['month'][:3]], int(match['day'])))
        if len(zips) != 1 or len(dates) != 2 or len(rooms) != 1 or not 1 <= rooms[0] <= 10:
            return None
        if not 1 <= (dates[1] - dates[0]).days <= 14:
            return None
        amounts = re.findall(r'(?:\$|\busd\s*)(\d+(?:,\d{3})*(?:\.\d{1,2})?)(?![\d.])', q)
        # Reject unsupported currency/ambiguous budget wording instead of dropping it.
        if re.search(r'[€£]|-\s*\$|\$\s*-', q):
            return None
        if not amounts and re.search(r'\bbudget|\baffordable|\bcheap|\bdollars|\bunder\b|at most|less than|maximum|no more than|\$', q):
            return None
        if len(amounts) > 1:
            return None
        budget = None
        kind = 'none'
        if amounts:
            nightly = bool(re.search(r'per\s+night|nightly|/night|a\s+night', q))
            total = bool(re.search(r'\btotal\b|entire\s+stay|whole\s+stay', q))
            if nightly == total or (nightly and rooms[0] > 1 and not re.search(r'per\s+room|/room', q)):
                return None
            budget = int(Decimal(amounts[0].replace(',', '')) * 100)
            kind = 'nightly_per_room' if nightly else 'total_stay'
        return StayIntent(postcode=next(iter(zips)), check_in=dates[0].isoformat(), check_out=dates[1].isoformat(),
                          rooms=rooms[0], budget_cents=budget, budget_type=kind)
    except (ValueError, OverflowError):
        return None


def verify_records(proposed, expected):
    """Reject omissions, duplicates, fabricated values and unexpected projection."""
    def normalized(rows):
        return sorted(json.dumps(r, sort_keys=True, ensure_ascii=False, allow_nan=False) for r in rows)
    if proposed.columns != COLUMNS or expected.columns != COLUMNS or normalized(proposed.records) != normalized(expected.records):
        raise RetrievalError('query_rejected')


def assess(intent, records):
    start, end = date.fromisoformat(intent.check_in), date.fromisoformat(intent.check_out)
    requested = [(start + timedelta(days=i)).isoformat() for i in range((end-start).days)]
    grouped = {}
    for row in records:
        hotel = grouped.setdefault(row['hotel_id'], {'hotel_id': row['hotel_id'], 'name': row['name'], 'nights': []})
        if row['stay_date'] is not None:
            hotel['nights'].append({k: row[k] for k in ('stay_date', 'nightly_rate_cents', 'rooms_available')})
    facts = []
    for hotel in grouped.values():
        nights = sorted(hotel['nights'], key=lambda n: n['stay_date'])
        missing = sorted(set(requested) - {n['stay_date'] for n in nights})
        if any(type(n[k]) is not int or n[k] < 0 for n in nights for k in ('nightly_rate_cents', 'rooms_available')):
            raise RetrievalError('query_rejected')
        complete = not missing
        enough = complete and all(n['rooms_available'] >= intent.rooms for n in nights)
        room_total = sum(n['nightly_rate_cents'] for n in nights) if complete else None
        total = room_total * intent.rooms if complete else None
        budget_ok = complete and (intent.budget_type == 'none' or
            (intent.budget_type == 'total_stay' and total <= intent.budget_cents) or
            (intent.budget_type == 'nightly_per_room' and all(n['nightly_rate_cents'] <= intent.budget_cents for n in nights)))
        facts.append({**hotel, 'nights': nights, 'missing_dates': missing, 'complete': complete,
                      'rooms_requested': intent.rooms, 'min_rooms_available': min((n['rooms_available'] for n in nights), default=None),
                      'room_total_cents': room_total, 'total_cents': total,
                      'enough_rooms': enough, 'within_budget': budget_ok, 'eligible': enough and budget_ok})
    facts.sort(key=lambda h: (not h['eligible'], h['total_cents'] if h['total_cents'] is not None else float('inf'), h['hotel_id']))
    status = 'answer' if any(h['eligible'] for h in facts) else 'insufficient_data' if any(not h['complete'] for h in facts) else 'no_matches'
    return status, facts


def render_answer(decision, status, facts, intent):
    """Render the LLM's checked structured recommendation, not unchecked free prose."""
    eligible = {h['hotel_id']: h for h in facts if h['eligible']}
    ids = [r.hotel_id for r in decision.recommendations]
    if decision.status != status or len(ids) != len(set(ids)) or any(i not in eligible for i in ids):
        raise ValueError('Ungrounded answer')
    if (status == 'answer') != bool(ids):
        raise ValueError('Missing or unexpected recommendation')
    if status == 'no_matches':
        return 'No saved hotels match this stay, room count and budget. Try another ZIP, date range or budget.'
    if status == 'insufficient_data':
        missing = sorted({d for h in facts for d in h['missing_dates']})
        return 'Saved nightly data is incomplete for ' + ', '.join(missing) + '. A complete stay and total cost cannot be confirmed.'
    parts = []
    for recommendation in decision.recommendations:
        h = eligible[recommendation.hotel_id]
        reason = recommendation.reason
        if reason == 'lowest_total' and h['total_cents'] != min(v['total_cents'] for v in eligible.values()):
            raise ValueError('Incorrect cheapest claim')
        if reason == 'more_rooms' and (h['min_rooms_available'] != max(v['min_rooms_available'] for v in eligible.values()) or
                                     len({v['min_rooms_available'] for v in eligible.values()}) < 2):
            raise ValueError('Incorrect room comparison')
        explanation = {'lowest_total': 'it has the lowest matching total',
                       'more_rooms': 'it has more rooms available than another matching hotel',
                       'meets_requirements': 'it meets your dates, room count and budget'}[reason]
        name = h['name'] or 'Hotel name not provided'
        parts.append(f"{name}: {intent.check_in} to {intent.check_out}, "
                     f"{len(h['nights'])} nights, {intent.rooms} room(s), ${h['total_cents']/100:.2f} total; "
                     f"at least {h['min_rooms_available']} rooms on every night. Recommended because {explanation}." )
    return '\n'.join(parts) + '\nCheckout is excluded. Comparisons cover only saved hotels; all amounts and availability are simulated.'
