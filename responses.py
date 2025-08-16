import random

annoying_truck = "Ein EuroCombi (deutscher Name Lang-LKW, Lang-Lkw, auch Megaliner) ist ein 'überlanger Lastkraftwagen', eine lange Lkw-Kombination mit bis zu 25,25 m Fahrzeuglänge und bis zu 60 t (bundesweiter Feldversuch in Deutschland 44 t) Gesamtgewicht. Es ist ein in Teilen Europas zugelassener Lkw-Typ, der die übliche Längenbegrenzung von 18,75 m überschreitet. Gemäß der EG-Richtlinie 96/53/EG kann diese große Fahrzeugkombination in den Staaten der Europäischen Union erlaubt werden. Schon seit 1970 gibt es in Finnland und Schweden die Fahrzeuggattung EuroCombi, deren Gewicht bis zu 60 Tonnen beträgt, und es wurde erforderlich, Maße und Gewichte von Lkw in der EU bzw. im Europäischen Wirtschaftsraum (EWR) weiter zu harmonisieren. In den anderen EWR-Mitgliedsländern werden noch einige Untersuchungen bzw. Großversuche absolviert."

other = [
    "Bist du dumm?", "Drück dich normal aus!", "Hallo, ich benutze WhatsApp!",
    "Kein Payback für dich.", "Du slayst heute gar nicht", annoying_truck
]


def handle_response(message) -> str:
  message = message.lower()

  if message[0] != "!":
    return ""

  if message == "deals":
    #return "Halt's Maul"
    return "Deals gibt es noch nicht. Sehe ich aus, als hätte ich was mit Payback zu tun??"
  elif message == "finn":
    return "Ich liebe Finn <3"
  elif message == "nick":
    return "pezetra"
  elif message == "nicole":
    return "random nudes"
  elif "baypack" in message.lower() or "payback" in message.lower():
    return ":eyes:"
  elif "maul" in message.lower():
    return "Ich schwöre, du kriegst gleich auf die Fresse"
  elif message == "slay" or message == "purr":
    return "PURRRRRRRRR"
  elif "orp" in message.lower():
    return "pew pew pew pew :boom: :bomb:"
  else:
    return random.choice(other)
