"""
Static reference data used by the map / logo features.

IMPORTANT: this sandbox has no internet access, so these stadium
coordinates and club colors are hand-curated static facts (public
knowledge, e.g. stadium locations), not pulled from a live API. They are
accurate as of the 2024/25 season but will not automatically reflect a
club moving grounds in the future -- update this dict if that happens.
"""
from __future__ import annotations

from typing import Dict, Optional, TypedDict


class StadiumInfo(TypedDict):
    stadium: str
    city: str
    lat: float
    lon: float
    capacity: int


STADIUMS: Dict[str, StadiumInfo] = {
    "Arsenal": {"stadium": "Emirates Stadium", "city": "London", "lat": 51.5549, "lon": -0.1084, "capacity": 60704},
    "Aston Villa": {"stadium": "Villa Park", "city": "Birmingham", "lat": 52.5091, "lon": -1.8848, "capacity": 42918},
    "Birmingham": {"stadium": "St Andrew's", "city": "Birmingham", "lat": 52.4758, "lon": -1.8683, "capacity": 29409},
    "Blackburn": {"stadium": "Ewood Park", "city": "Blackburn", "lat": 53.7286, "lon": -2.4891, "capacity": 31367},
    "Blackpool": {"stadium": "Bloomfield Road", "city": "Blackpool", "lat": 53.8046, "lon": -3.0483, "capacity": 16220},
    "Bolton": {"stadium": "University of Bolton Stadium", "city": "Bolton", "lat": 53.5943, "lon": -2.5359, "capacity": 28723},
    "Bournemouth": {"stadium": "Vitality Stadium", "city": "Bournemouth", "lat": 50.7352, "lon": -1.8384, "capacity": 11364},
    "Bradford": {"stadium": "Valley Parade", "city": "Bradford", "lat": 53.8064, "lon": -1.7592, "capacity": 25136},
    "Brentford": {"stadium": "Gtech Community Stadium", "city": "London", "lat": 51.4907, "lon": -0.2887, "capacity": 17250},
    "Brighton": {"stadium": "American Express Stadium", "city": "Brighton", "lat": 50.8617, "lon": -0.0834, "capacity": 31800},
    "Burnley": {"stadium": "Turf Moor", "city": "Burnley", "lat": 53.7890, "lon": -2.2302, "capacity": 21944},
    "Cardiff": {"stadium": "Cardiff City Stadium", "city": "Cardiff", "lat": 51.4728, "lon": -3.2030, "capacity": 33280},
    "Charlton": {"stadium": "The Valley", "city": "London", "lat": 51.4861, "lon": 0.0364, "capacity": 27111},
    "Chelsea": {"stadium": "Stamford Bridge", "city": "London", "lat": 51.4816, "lon": -0.1909, "capacity": 40343},
    "Coventry": {"stadium": "Coventry Building Society Arena", "city": "Coventry", "lat": 52.4487, "lon": -1.4954, "capacity": 32609},
    "Crystal Palace": {"stadium": "Selhurst Park", "city": "London", "lat": 51.3983, "lon": -0.0855, "capacity": 25486},
    "Derby": {"stadium": "Pride Park", "city": "Derby", "lat": 52.9148, "lon": -1.4474, "capacity": 33597},
    "Everton": {"stadium": "Goodison Park", "city": "Liverpool", "lat": 53.4388, "lon": -2.9663, "capacity": 39572},
    "Fulham": {"stadium": "Craven Cottage", "city": "London", "lat": 51.4749, "lon": -0.2216, "capacity": 29600},
    "Huddersfield": {"stadium": "John Smith's Stadium", "city": "Huddersfield", "lat": 53.6543, "lon": -1.7684, "capacity": 24121},
    "Hull": {"stadium": "MKM Stadium", "city": "Hull", "lat": 53.7461, "lon": -0.3665, "capacity": 25586},
    "Ipswich": {"stadium": "Portman Road", "city": "Ipswich", "lat": 52.0552, "lon": 1.1451, "capacity": 30311},
    "Leeds": {"stadium": "Elland Road", "city": "Leeds", "lat": 53.7778, "lon": -1.5722, "capacity": 37792},
    "Leicester": {"stadium": "King Power Stadium", "city": "Leicester", "lat": 52.6204, "lon": -1.1422, "capacity": 32261},
    "Liverpool": {"stadium": "Anfield", "city": "Liverpool", "lat": 53.4308, "lon": -2.9608, "capacity": 61276},
    "Luton": {"stadium": "Kenilworth Road", "city": "Luton", "lat": 51.8843, "lon": -0.4324, "capacity": 10356},
    "Man City": {"stadium": "Etihad Stadium", "city": "Manchester", "lat": 53.4831, "lon": -2.2004, "capacity": 53400},
    "Man United": {"stadium": "Old Trafford", "city": "Manchester", "lat": 53.4631, "lon": -2.2913, "capacity": 74310},
    "Middlesbrough": {"stadium": "Riverside Stadium", "city": "Middlesbrough", "lat": 54.5786, "lon": -1.2169, "capacity": 34742},
    "Newcastle": {"stadium": "St James' Park", "city": "Newcastle", "lat": 54.9756, "lon": -1.6217, "capacity": 52305},
    "Norwich": {"stadium": "Carrow Road", "city": "Norwich", "lat": 52.6221, "lon": 1.3092, "capacity": 27359},
    "Nott'm Forest": {"stadium": "The City Ground", "city": "Nottingham", "lat": 52.9399, "lon": -1.1327, "capacity": 30445},
    "Portsmouth": {"stadium": "Fratton Park", "city": "Portsmouth", "lat": 50.7989, "lon": -1.0637, "capacity": 21100},
    "QPR": {"stadium": "Loftus Road", "city": "London", "lat": 51.5090, "lon": -0.2323, "capacity": 18439},
    "Reading": {"stadium": "Select Car Leasing Stadium", "city": "Reading", "lat": 51.4222, "lon": -0.9827, "capacity": 24161},
    "Sheffield United": {"stadium": "Bramall Lane", "city": "Sheffield", "lat": 53.3701, "lon": -1.4708, "capacity": 32050},
    "Southampton": {"stadium": "St Mary's Stadium", "city": "Southampton", "lat": 50.9058, "lon": -1.3910, "capacity": 32384},
    "Stoke": {"stadium": "bet365 Stadium", "city": "Stoke-on-Trent", "lat": 52.9885, "lon": -2.1754, "capacity": 30089},
    "Sunderland": {"stadium": "Stadium of Light", "city": "Sunderland", "lat": 54.9144, "lon": -1.3883, "capacity": 48707},
    "Swansea": {"stadium": "Swansea.com Stadium", "city": "Swansea", "lat": 51.6425, "lon": -3.9350, "capacity": 21088},
    "Tottenham": {"stadium": "Tottenham Hotspur Stadium", "city": "London", "lat": 51.6043, "lon": -0.0664, "capacity": 62850},
    "Watford": {"stadium": "Vicarage Road", "city": "Watford", "lat": 51.6497, "lon": -0.4013, "capacity": 22200},
    "West Brom": {"stadium": "The Hawthorns", "city": "West Bromwich", "lat": 52.5091, "lon": -1.9640, "capacity": 26850},
    "West Ham": {"stadium": "London Stadium", "city": "London", "lat": 51.5386, "lon": -0.0166, "capacity": 62500},
    "Wigan": {"stadium": "DW Stadium", "city": "Wigan", "lat": 53.5478, "lon": -2.6524, "capacity": 25133},
    "Wolves": {"stadium": "Molineux Stadium", "city": "Wolverhampton", "lat": 52.5903, "lon": -2.1300, "capacity": 32050},
}

# Simple deterministic color per club (used for logo-placeholder badges and
# chart color-mapping) since we cannot fetch real crest images offline.
TEAM_COLORS: Dict[str, str] = {
    "Arsenal": "#EF0107", "Aston Villa": "#95BFE5", "Birmingham": "#0000FF",
    "Blackburn": "#009EE0", "Blackpool": "#FF6600", "Bolton": "#8C181A",
    "Bournemouth": "#DA291C", "Bradford": "#800000", "Brentford": "#E30613",
    "Brighton": "#0057B8", "Burnley": "#6C1D45", "Cardiff": "#0070B5",
    "Charlton": "#D2122E", "Chelsea": "#034694", "Coventry": "#78D0F7",
    "Crystal Palace": "#1B458F", "Derby": "#000000", "Everton": "#003399",
    "Fulham": "#000000", "Huddersfield": "#0E63AD", "Hull": "#F18A01",
    "Ipswich": "#0044A9", "Leeds": "#FFCD00", "Leicester": "#003090",
    "Liverpool": "#C8102E", "Luton": "#F78F1E", "Man City": "#6CABDD",
    "Man United": "#DA291C", "Middlesbrough": "#E21C21", "Newcastle": "#241F20",
    "Norwich": "#00A650", "Nott'm Forest": "#DD0000", "Portsmouth": "#001489",
    "QPR": "#1D5BA4", "Reading": "#004494", "Sheffield United": "#EE2737",
    "Southampton": "#D71920", "Stoke": "#E03A3E", "Sunderland": "#EB172B",
    "Swansea": "#121212", "Tottenham": "#132257", "Watford": "#FBEE23",
    "West Brom": "#122F67", "West Ham": "#7A263A", "Wigan": "#1D59AF",
    "Wolves": "#FDB913",
}


def get_stadium(team: str) -> Optional[StadiumInfo]:
    return STADIUMS.get(team)


def get_team_color(team: str) -> str:
    return TEAM_COLORS.get(team, "#7b2ff7")


# --------------------------------------------------------------------------- #
# Image assets: club logos, stadium photos, competition logo
# --------------------------------------------------------------------------- #
import os

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
_LOGO_DIR = os.path.join(_ASSETS_DIR, "club_logos")
_STADIUM_IMG_DIR = os.path.join(_ASSETS_DIR, "stadiums")
_IMAGES_DIR = os.path.join(_ASSETS_DIR, "images")

# CSV team name -> exact logo filename (as downloaded). Update this dict if
# you rename or add files in assets/club_logos/.
LOGO_FILENAMES: Dict[str, str] = {
    "Arsenal": "arsenal.png", "Aston Villa": "aston_villa.png", "Birmingham": "birmingham.png",
    "Blackburn": "blackburn.png", "Blackpool": "blackpool.png", "Bolton": "bolton.png",
    "Bournemouth": "bournemouth.png", "Bradford": "bradford.png", "Brentford": "brentford.png",
    "Brighton": "brighton.png", "Burnley": "burnley.png", "Cardiff": "cardiff-city.png",
    "Charlton": "charlton.png", "Chelsea": "chelsea.png", "Coventry": "coventry.png",
    "Crystal Palace": "crystal_palace.png", "Derby": "derby.png", "Everton": "everton.png",
    "Fulham": "fulham.png", "Huddersfield": "huddersfield.png", "Hull": "hull.png",
    "Ipswich": "ipswich.png", "Leeds": "leeds.png", "Leicester": "leicester.png",
    "Liverpool": "liverpool.png", "Luton": "luton.png", "Man City": "man_city.png",
    "Man United": "man_united.png", "Middlesbrough": "middlesbrough.png", "Newcastle": "newcastle.png",
    "Norwich": "norwich.png", "Nott'm Forest": "nott'm_forest.png", "Portsmouth": "portsmouth.png",
    "QPR": "qpr.png", "Reading": "reading.png", "Sheffield United": "sheffield_united.png",
    "Southampton": "southampton.png", "Stoke": "stoke.png", "Sunderland": "sunderland.png",
    "Swansea": "swansea.png", "Tottenham": "tottenham.png", "Watford": "watford.png",
    "West Brom": "west_brom.png", "West Ham": "west_ham.png", "Wigan": "wigan.png",
    "Wolves": "wolves.png",
}

# CSV team name -> exact stadium-photo filename (as downloaded). These are
# named after the stadium/city, not the club, so this mapping is separate
# from LOGO_FILENAMES above.
STADIUM_IMAGE_FILENAMES: Dict[str, str] = {
    "Arsenal": "Emirates_Stadium_London.png",
    "Aston Villa": "Villa_Park_Birmingham.png",
    "Birmingham": "St_Andrew's_Birmingham.png",
    "Blackburn": "Ewood_Park_Blackburn.png",
    "Blackpool": "Bloomfield_Road_Blackpool.png",
    "Bolton": "University_of_Bolton_Stadium_Bolton.png",
    "Bournemouth": "Vitality_Stadium_Bournemouth.png",
    "Bradford": "Valley_Parade_Bradford.png",
    "Brentford": "Gtech_Community_Stadium_London.png",
    "Brighton": "American_Express_Stadium_Brighton.png",
    "Burnley": "Turf_Moor_Burnley.png",
    "Cardiff": "Cardiff_City_Stadium_Cardiff.png",
    "Charlton": "The_Valley_London.png",
    "Chelsea": "Stamford_Bridge_London.png",
    "Coventry": "Coventry_Building_Society_Arena_Coventry.png",
    "Crystal Palace": "Selhurst_Park_London.png",
    "Derby": "Pride_Park_Derby.png",
    "Everton": "Goodison_Park_Liverpool.png",
    "Fulham": "Craven_Cottage_London.png",
    "Huddersfield": "John_Smith's_Stadium_Huddersfield.png",
    "Hull": "MKM_Stadium_Hull.png",
    "Ipswich": "Portman_Road_Ipswich.png",
    "Leeds": "Elland_Road_Leeds.png",
    "Leicester": "King_Power_Stadium_Leicester.png",
    "Liverpool": "Anfield_Liverpool.png",
    "Luton": "Kenilworth_Road_Luton.png",
    "Man City": "Etihad_Stadium_Manchester.png",
    "Man United": "Old_Trafford, Manchester.png",
    "Middlesbrough": "Riverside_Stadium_Middlesbrough.png",
    "Newcastle": "St_James'_Park_Newcastle.png",
    "Norwich": "Carrow_Road_Norwich.png",
    "Nott'm Forest": "The_City_Ground_Nottingham.png",
    "Portsmouth": "Fratton_Park_Portsmouth.png",
    "QPR": "Loftus_Road_London.png",
    "Reading": "Select_Car_Leasing_Stadium_Reading.png",
    "Sheffield United": "Bramall_Lane_Sheffield.png",
    "Southampton": "St_Mary's_Stadium_Southampton.png",
    "Stoke": "bet365_Stadium_Stoke_on_Trent.png",
    "Sunderland": "Stadium_of_Light_Sunderland.png",
    "Swansea": "Swansea.com_Stadium_Swansea.png",
    "Tottenham": "Tottenham_Hotspur_Stadium_London.png",
    "Watford": "Vicarage_Road_Watford.png",
    "West Brom": "The_Hawthorns_West_Bromwich.png",
    "West Ham": "London_Stadium_London.png",
    "Wigan": "DW_Stadium_Wigan.png",
    "Wolves": "Molineux_Stadium_Wolverhampton.png",
}


def _resolve_path(directory: str, filename: Optional[str]) -> Optional[str]:
    """Return the full path if the file actually exists on disk, else None
    -- callers should fall back to a placeholder badge/text when this
    returns None instead of crashing."""
    if not filename:
        return None
    path = os.path.join(directory, filename)
    return path if os.path.exists(path) else None


def get_logo_path(team: str) -> Optional[str]:
    """Full filesystem path to a team's crest PNG, or None if not found on
    disk (caller should show the color-badge fallback in that case)."""
    return _resolve_path(_LOGO_DIR, LOGO_FILENAMES.get(team))


def get_stadium_image_path(team: str) -> Optional[str]:
    """Full filesystem path to a team's stadium photo, or None if missing."""
    return _resolve_path(_STADIUM_IMG_DIR, STADIUM_IMAGE_FILENAMES.get(team))


def get_competition_logo_path() -> Optional[str]:
    """
    Full filesystem path to the Premier League logo in assets/images/, if
    present. Tries a few common filenames so it works regardless of exactly
    what you named the download.
    """
    candidates = [
        "premier_league.png", "premier-league.png", "Premier_League.png",
        "PremierLeague.png", "pl_logo.png", "premier_league_logo.png",
    ]
    if os.path.isdir(_IMAGES_DIR):
        for fname in os.listdir(_IMAGES_DIR):
            if "premier" in fname.lower() and fname.lower().endswith((".png", ".jpg", ".jpeg", ".svg")):
                return os.path.join(_IMAGES_DIR, fname)
    for c in candidates:
        resolved = _resolve_path(_IMAGES_DIR, c)
        if resolved:
            return resolved
    return None