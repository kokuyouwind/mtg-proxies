import requests
from mtgproxies.decklists import Decklist
from mtgproxies.decklists.sanitizing import validate_card_name, validate_print


def parse_decklist(manastack_id: str, zones=["commander", "mainboard"]):
    """Parse a decklist from manastack.

    Args:
        manastack_id: Deck list id as shown in the bdeckbuilder URL
        zones: List of zones to include. Available are: `mainboard`, `commander`, `sideboard` and `maybeboard`
    """
    decklist = Decklist()
    warnings = []
    ok = True

    r = requests.get(f"https://manastack.com/api/decklist?format=json&id={manastack_id}")
    if r.status_code != 200:
        raise (ValueError(f"Manastack returned statuscode {r.status_code}"))

    data = r.json()["list"]
    for zone in zones:
        if len(data[zone]) > 0:
            decklist.append_comment(zone.capitalize())
            for item in data[zone]:
                # Extract relevant data
                count = item['count']
                card_name = item['card']['name']
                set_id = item['card']['set']['slug']
                collector_number = item['card']['num']

                # Validate card name
                card_name, warnings_name = validate_card_name(card_name)
                if card_name is None:
                    decklist.append_comment(card_name)
                    warnings.extend([(decklist.entries[-1], w) for w in warnings_name])
                    ok = False
                    continue

                # Validate card print
                card, warnings_print = validate_print(card_name, set_id, collector_number, warn_quality=False)

                decklist.append_card(count, card)
                warnings.extend([(decklist.entries[-1], w) for w in warnings_name + warnings_print])

            decklist.append_comment("")

    return decklist, ok, warnings
