"""
MIT License

Copyright (c) 2021-present MrArkon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from dateutil.parser import isoparse


__all__ = ["Anime", "Genre"]


class Anime:
    """Represents an anime object returned by the API."""

    def __init__(self, payload: dict) -> None:
        self._payload: dict = payload.get("data", {}) or payload
        self._included_payload: List[dict] = payload.get("included", [])

    def __repr__(self) -> str:
        title = self.title or "Unknown Anime"
        return f"<Anime id={self.id} title='{title}'>"

    @property
    def id(self) -> str:
        return self._payload.get("id", "")

    @property
    def created_at(self) -> Optional[datetime]:
        try:
            return isoparse(self._payload["attributes"]["createdAt"])
        except (KeyError, TypeError):
            return None

    @property
    def updated_at(self) -> Optional[datetime]:
        try:
            return isoparse(self._payload["attributes"]["updatedAt"])
        except (KeyError, TypeError):
            return None

    @property
    def slug(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["slug"]
        except KeyError:
            return None

    @property
    def synopsis(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["synopsis"]
        except KeyError:
            return None

    @property
    def title(self) -> Optional[str]:
        """Returns the first available localized title, falling back to canonical."""
        _TITLE_PRIORITY = ("en", "en_jp", "ja_jp")
        try:
            titles = self._payload["attributes"]["titles"]
            for key in _TITLE_PRIORITY:
                if titles.get(key):
                    return titles[key]
            return self.canonical_title
        except KeyError:
            return None

    @property
    def japanese_title(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["titles"].get("en_jp")
        except KeyError:
            return None

    @property
    def romaji_title(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["titles"].get("ja_jp")
        except KeyError:
            return None

    @property
    def canonical_title(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["canonicalTitle"]
        except KeyError:
            return None

    @property
    def abbreviated_titles(self) -> List[str]:
        try:
            return self._payload["attributes"]["abbreviatedTitles"]
        except KeyError:
            return []

    @property
    def average_rating(self) -> Optional[float]:
        try:
            return float(self._payload["attributes"]["averageRating"])
        except (KeyError, TypeError):
            return None

    @property
    def rating_frequencies(self) -> Optional[Dict[str, str]]:
        try:
            return self._payload["attributes"]["ratingFrequencies"]
        except KeyError:
            return None

    @property
    def user_count(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["userCount"])
        except (KeyError, TypeError):
            return None

    @property
    def favorites_count(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["favoritesCount"])
        except (KeyError, TypeError):
            return None

    @property
    def start_date(self) -> Optional[datetime]:
        try:
            return datetime.strptime(self._payload["attributes"]["startDate"], "%Y-%m-%d")
        except (KeyError, TypeError):
            return None

    @property
    def end_date(self) -> Optional[datetime]:
        try:
            return datetime.strptime(self._payload["attributes"]["endDate"], "%Y-%m-%d")
        except (KeyError, TypeError):
            return None

    @property
    def popularity_rank(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["popularityRank"])
        except (KeyError, TypeError):
            return None

    @property
    def rating_rank(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["ratingRank"])
        except (KeyError, TypeError):
            return None

    @property
    def age_rating(self) -> Optional[Literal["G", "PG", "R", "R18"]]:
        try:
            return self._payload["attributes"]["ageRating"]
        except KeyError:
            return None

    @property
    def age_rating_guide(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["ageRatingGuide"]
        except KeyError:
            return None

    @property
    def subtype(self) -> Optional[Literal["ONA", "OVA", "TV", "movie", "music", "special"]]:
        try:
            return self._payload["attributes"]["subtype"]
        except KeyError:
            return None

    @property
    def status(self) -> Optional[Literal["current", "finished", "tba", "unreleased", "upcoming"]]:
        try:
            return self._payload["attributes"]["status"]
        except KeyError:
            return None

    @property
    def tba(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["tba"]
        except KeyError:
            return None

    def poster_image(
        self, _type: Optional[Literal["tiny", "small", "medium", "large", "original"]] = "original"
    ) -> Optional[str]:
        try:
            return self._payload["attributes"]["posterImage"].get(_type)
        except AttributeError:
            return None

    def cover_image(self, _type: Optional[Literal["tiny", "small", "large", "original"]] = "original") -> Optional[str]:
        try:
            return self._payload["attributes"]["coverImage"].get(_type)
        except AttributeError:
            return None

    @property
    def episodes(self) -> List[Episode]:
        """
        Returns only the episodes included in the response.

        If no episodes are included, an empty list is returned.
        The include="episodes" query parameter is required for episodes to be included.
        """
        try:
            included = self._included_payload or []
            return [Episode(item) for item in included if item["type"] == "episodes"]
        except KeyError:
            return []
        except TypeError:
            return []

    @property
    def episode_count(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["episodeCount"])
        except (KeyError, TypeError):
            return None

    @property
    def episode_length(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["episodeLength"])
        except (KeyError, TypeError):
            return None

    @property
    def total_length(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["totalLength"])
        except (KeyError, TypeError):
            return None

    @property
    def yt_video_id(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["youtubeVideoId"]
        except KeyError:
            return None

    @property
    def nsfw(self) -> bool:
        """Returns True if the anime is NSFW. Otherwise, False. Defaults to False when not present in the API response."""
        try:
            return self._payload["attributes"]["nsfw"]
        except KeyError:
            return False

    @property
    def raw(self) -> dict:
        """Returns the JSON response from the API."""
        return self._payload

    @property
    def genres(self) -> List[Genre]:
        included = self._included_payload or []
        return [Genre(item) for item in included if item["type"] == "genres"]


class Episode:
    """Represents an episode object returned by the API."""

    def __init__(self, payload: dict) -> None:
        self._payload: dict = payload

    @property
    def id(self) -> str:
        return self._payload.get("id", "")

    @property
    def created_at(self) -> Optional[datetime]:
        try:
            return isoparse(self._payload["attributes"]["createdAt"])
        except (KeyError, TypeError):
            return None

    @property
    def updated_at(self) -> Optional[datetime]:
        try:
            return isoparse(self._payload["attributes"]["updatedAt"])
        except (KeyError, TypeError):
            return None

    @property
    def synopsis(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["synopsis"]
        except KeyError:
            return None

    @property
    def description(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["description"]
        except KeyError:
            return None

    @property
    def english_title(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["titles"].get("en_us")
        except KeyError:
            return f"Episode {self.number}" if self.number else None

    @property
    def japanese_title(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["titles"].get("en_jp")
        except KeyError:
            return f"Episode {self.number}" if self.number else None

    @property
    def romaji_title(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["titles"].get("ja_jp")
        except KeyError:
            return f"Episode {self.number}" if self.number else None

    @property
    def canonical_title(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["canonicalTitle"]
        except KeyError:
            return f"Episode {self.number}" if self.number else None

    @property
    def season(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["seasonNumber"])
        except (KeyError, TypeError):
            return None

    @property
    def number(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["number"])
        except (KeyError, TypeError):
            return None

    @property
    def relative_number(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["relativeNumber"])
        except (KeyError, TypeError):
            return None

    @property
    def air_date(self) -> Optional[datetime]:
        try:
            return isoparse(self._payload["attributes"]["airdate"])
        except (KeyError, TypeError):
            return None

    @property
    def length(self) -> Optional[int]:
        try:
            return int(self._payload["attributes"]["length"])
        except (KeyError, TypeError):
            return None

    @property
    def thumbnail(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["thumbnail"]["original"]
        except (KeyError, TypeError):
            return None

    @property
    def raw(self) -> dict:
        """Returns the JSON response from the API."""
        return self._payload

    def __repr__(self) -> str:
        title = self.canonical_title or "Unknown Episode"
        return f"<Episode id={self.id} title='{title}'>"


class Genre:
    """Represents a genre objct returned by the API."""

    def __init__(self, payload: dict) -> None:
        self._payload: dict = payload

    def __repr__(self) -> str:
        name = self.name or "Unknown Genre"
        return f"<Genre id={self.id} title='{name}'>"

    @property
    def id(self) -> str:
        return self._payload.get("id", "")

    @property
    def name(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["name"]
        except KeyError:
            return None

    @property
    def slug(self) -> Optional[str]:
        try:
            return self._payload["attributes"]["slug"]
        except KeyError:
            return None

    @property
    def raw(self) -> dict:
        """Returns the JSON response from the API."""
        return self._payload
