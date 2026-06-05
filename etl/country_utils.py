from __future__ import annotations

import re
import unicodedata


def ascii_fold(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text)
    return text.upper()


COUNTRY_ALIASES = {
    "ALEMANIA": "Alemania",
    "ARGENTINA": "Argentina",
    "AUSTRALIA": "Australia",
    "AUTRALIA": "Australia",
    "AUSTRIA": "Austria",
    "BELGICA": "Bélgica",
    "BOLIVIA": "Bolivia",
    "BOSNIA HERZEGOVINA": "Bosnia y Herzegovina",
    "BOSNIA-HERZEGOVINA": "Bosnia y Herzegovina",
    "BRASIL": "Brasil",
    "CANADA": "Canadá",
    "CANAD": "Canadá",
    "CHILE": "Chile",
    "CHINA": "China",
    "COLOMBIA": "Colombia",
    "COREA": "Corea del Sur",
    "COSTA RICA": "Costa Rica",
    "CROACIA": "Croacia",
    "CUBA": "Cuba",
    "DINAMARCA": "Dinamarca",
    "ECUADOR": "Ecuador",
    "EGIPTO": "Egipto",
    "EL SALVADOR": "El Salvador",
    "ESLOVAQUIA": "Eslovaquia",
    "ESPAA": "España",
    "ESPANA": "España",
    "ESTADOS UNIDOS": "Estados Unidos",
    "ESTADOS UNIDOS DE AMERICA": "Estados Unidos",
    "ESTADOS UNIDOS DE AMRICA": "Estados Unidos",
    "ESTONIA": "Estonia",
    "FEDERACION RUSA": "Rusia",
    "FINLANDIA": "Finlandia",
    "FRANCIA": "Francia",
    "GRECIA": "Grecia",
    "GUATEMALA": "Guatemala",
    "HOLANDA": "Países Bajos",
    "HONG KONG": "Hong Kong",
    "HUNGRIA": "Hungría",
    "INDIA": "India",
    "INDONESIA": "Indonesia",
    "INGLATERRA": "Reino Unido",
    "IRLANDA": "Irlanda",
    "ISLANDIA": "Islandia",
    "ISRAEL": "Israel",
    "ITALIA": "Italia",
    "JAPON": "Japón",
    "LETONIA": "Letonia",
    "LITUANIA": "Lituania",
    "LUXEMBURGO": "Luxemburgo",
    "MALASIA": "Malasia",
    "N/D": None,
    "NORUEGA": "Noruega",
    "NUEVA ZELANDA": "Nueva Zelanda",
    "PAISES BAJOS": "Países Bajos",
    "PASES BAJOS": "Países Bajos",
    "PANAMA": "Panamá",
    "PERU": "Perú",
    "POLONIA": "Polonia",
    "PORTUGAL": "Portugal",
    "PUERTO RICO": "Puerto Rico",
    "REINO UNIDO": "Reino Unido",
    "REP. CHECA": "República Checa",
    "REPUBLICA CHECA": "República Checa",
    "REP. DE COREA": "Corea del Sur",
    "REPUBLICA DOMINICANA": "República Dominicana",
    "RUSIA": "Rusia",
    "SINGAPUR": "Singapur",
    "SUDAFRICA": "Sudáfrica",
    "SUECIA": "Suecia",
    "SUIZA": "Suiza",
    "TAILANDIA": "Tailandia",
    "TAIWAN": "Taiwán",
    "TURQUIA": "Turquía",
    "UCRANIA": "Ucrania",
    "URUGUAY": "Uruguay",
    "VIETNAM": "Vietnam",
}


COUNTRY_MAP_CODES = {
    "Alemania": "de",
    "Argentina": "ar",
    "Australia": "au",
    "Austria": "at",
    "Bélgica": "be",
    "Bolivia": "bo",
    "Bosnia y Herzegovina": "ba",
    "Brasil": "br",
    "Canadá": "ca",
    "Chile": "cl",
    "China": "cn",
    "Colombia": "co",
    "Corea del Sur": "kr",
    "Costa Rica": "cr",
    "Croacia": "hr",
    "Cuba": "cu",
    "Dinamarca": "dk",
    "Ecuador": "ec",
    "Egipto": "eg",
    "El Salvador": "sv",
    "Eslovaquia": "sk",
    "España": "es",
    "Estados Unidos": "us",
    "Estonia": "ee",
    "Finlandia": "fi",
    "Francia": "fr",
    "Grecia": "gr",
    "Guatemala": "gt",
    "Hong Kong": "cn",
    "Hungría": "hu",
    "India": "in",
    "Indonesia": "id",
    "Irlanda": "ie",
    "Islandia": "is",
    "Israel": "il",
    "Italia": "it",
    "Japón": "jp",
    "Letonia": "lv",
    "Lituania": "lt",
    "Luxemburgo": "lu",
    "Malasia": "my",
    "Noruega": "no",
    "Nueva Zelanda": "nz",
    "Países Bajos": "nl",
    "Panamá": "pa",
    "Perú": "pe",
    "Polonia": "pl",
    "Portugal": "pt",
    "Puerto Rico": "pr",
    "Reino Unido": "gb",
    "República Checa": "cz",
    "República Dominicana": "do",
    "Rusia": "ru",
    "Singapur": "sg",
    "Sudáfrica": "za",
    "Suecia": "se",
    "Suiza": "ch",
    "Tailandia": "th",
    "Taiwán": "tw",
    "Turquía": "tr",
    "Ucrania": "ua",
    "Uruguay": "uy",
    "Vietnam": "vn",
}


def normalize_country_value(value: object, catalog_value: str | None = None) -> str | None:
    folded = ascii_fold(value)
    if not folded:
        return None
    if folded in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[folded]
    if catalog_value:
        return catalog_value
    return str(value).strip().title()


def get_country_map_code(country_name: object) -> str | None:
    if country_name is None:
        return None
    return COUNTRY_MAP_CODES.get(str(country_name).strip())
