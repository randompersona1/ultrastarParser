from collections.abc import Callable
from typing import Optional
from functools import total_ordering


class AttributeMapping:
    def __init__(
        self,
        new_name: str,
        transform: Optional[Callable[[str, dict[str, str]], str]] | None = None,
    ) -> None:
        self.new_name = new_name
        self.transform = transform

    new_name: str
    # the callable takes the new value name and the attributes dict and returns the new value
    transform: Optional[Callable[[str, dict[str, str]], str]] | None = None


class VersionChangeError(ValueError):
    def __init__(
        self, version: "FormatVersion", message: str = "Unable to change version"
    ) -> None:
        self.version = version
        self.message = message
        super().__init__(f"{message}: {version}")


@total_ordering
class FormatVersion:
    major: int
    minor: int
    patch: int

    def __init__(self, version: str | tuple[int, int, int]) -> None:
        if isinstance(version, str):
            if version.startswith("v") or version.startswith("V"):
                version = version[1:]
            if "." not in version:
                raise ValueError("Invalid version format")
            self.major, self.minor, self.patch = map(int, version.split("."))
        else:
            self.major, self.minor, self.patch = version

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FormatVersion):
            return False
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, FormatVersion):
            return False
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch < other.patch

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch))


@total_ordering
class BaseUltrastarVersion:
    def __init__(self) -> None:
        self._version: FormatVersion
        self._attributes: dict[str, str] = {}
        self._body: list[str] = []

        self.primary_audio_attributes: str | None

        self.required_attributes: list[str]
        self.optional_attributes: list[str]
        self.attribute_mappings: dict[str, dict[str, AttributeMapping]]

    def parse(self, file: str) -> None:
        attributes = {}
        body = []

        lines = file.splitlines()
        if len(lines) < 1:
            return
        headerFinished: bool = False
        for line in lines:
            line = line.strip()
            if line.startswith("#") and not headerFinished:
                key, value = line[1:].split(":", 1)
                key = key.upper()
                attributes[key.strip()] = value.strip()
            elif line == "" and not headerFinished:
                continue
            elif (line is None or line.isspace()) and headerFinished:
                body.append(line)
            elif line == "E":
                break
            else:
                headerFinished = True
                body.append(line)

        self._set_attributes(attributes)
        self._set_body(body)

    def downgrade(self) -> "BaseUltrastarVersion":
        version_keys = list(versions.keys())
        current_index = version_keys.index(self._version)
        if current_index == 0:
            raise VersionChangeError(
                self.get_version(),
                "Cannot downgrade from version because it is the latest version.",
            )

        previous_version_key = version_keys[current_index - 1]
        previous_version_class: BaseUltrastarVersion = versions[previous_version_key]()

        attribute_mapping = self.attribute_mappings.get("downgrade", {})
        previous_version_class._attributes = {}
        for k, v in self._attributes.items():
            if k in attribute_mapping:
                mapping = attribute_mapping[k]
                new_key = mapping.new_name
                transform = mapping.transform
                previous_version_class._attributes[new_key] = (
                    transform(v) if transform else v
                )
            else:
                previous_version_class._attributes[k] = v

        previous_version_class._version = previous_version_key
        previous_version_class._attributes["VERSION"] = str(previous_version_key)
        previous_version_class._set_body(self._body)

        return previous_version_class

    def upgrade(self) -> "BaseUltrastarVersion":
        version_keys = list(versions.keys())
        current_index = version_keys.index(self._version)
        if current_index == len(version_keys) - 1:
            raise VersionChangeError(
                self.get_version(),
                "Cannot upgrade from version because it is the latest version.",
            )

        next_version_key = version_keys[current_index + 1]
        next_version_class: BaseUltrastarVersion = versions[next_version_key]()

        attribute_mapping = next_version_class.attribute_mappings.get("upgrade", {})
        next_version_class._attributes = {}
        next_version_class._version = next_version_key
        for k, v in self._attributes.items():
            if k in attribute_mapping:
                mapping = attribute_mapping[k]
                new_key = mapping.new_name
                transform = mapping.transform
                next_version_class._attributes[new_key] = (
                    transform(v) if transform else v
                )
            else:
                next_version_class._attributes[k] = v

        next_version_class._version = next_version_key
        next_version_class._attributes["VERSION"] = str(next_version_key)
        next_version_class._set_body(self._body)

        return next_version_class

    def _set_attributes(self, attributes: dict[str, str]) -> None:
        self._attributes = attributes

    def _set_body(self, body: list[str]) -> None:
        self._body = body

    def get_attributes(self) -> dict[str, str]:
        return self._attributes

    def get_attribute(self, attribute: str) -> str | None:
        if attribute in self._attributes:
            return self._attributes.get(attribute)
        return None

    def get_body(self) -> list[str]:
        return self._body

    def get_version(self) -> FormatVersion:
        return self._version

    def get_primary_audio(self) -> str | None:
        for key in self.primary_audio_attributes:
            if self.get_attribute(key) is not None:
                return self.get_attribute(key)
        else:
            return None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseUltrastarVersion):
            return False
        version_equal: bool = self.get_version() == other.get_version()
        attributes_equal: bool = self.get_attributes() == other.get_attributes()
        body_equal: bool = self.get_body() == other.get_body()

        return version_equal and attributes_equal and body_equal

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, BaseUltrastarVersion):
            return False
        return self.get_version() < other.get_version()


class UltrastarVersion010(BaseUltrastarVersion):
    _version: FormatVersion = FormatVersion("0.1.0")
    required_attributes = [
        "VERSION",
        "TITLE",
        "ARTIST",
        "MP3",
        "BPM",
    ]
    optional_attributes = []

    primary_audio_attributes = ["MP3"]


class UltrastarVersion020(BaseUltrastarVersion):
    _version: FormatVersion = FormatVersion("0.2.0")
    required_attributes = [
        "VERSION",
        "TITLE",
        "ARTIST",
        "MP3",
        "BPM",
    ]
    optional_attributes = [
        "GAP",
        "COVER",
        "BACKGROUND",
        "VIDEO",
        "VIDEOGAP",
        "GENRE",
        "EDITION",
        "CREATOR",
        "LANGUAGE",
        "YEAR",
        "START",
        "END",
        "PREVIEWSTART",
        "MEDLEYSTARTBEAT",
        "MEDLEYENDBEAT",
        "CALCMEDLEY",
        "DUETSINGERP1",
        "DUETSINGERP2",
        "P1",
        "P2",
        "COMMENT",
        "RESOLUTION",
        "NOTESGAP",
        "RELATIVE",
        "ENCODING",
    ]
    attribute_mappings = {}

    primary_audio_attributes = ["MP3"]


class UltrastarVersion030(BaseUltrastarVersion):
    _version: FormatVersion = FormatVersion("0.3.0")
    required_attributes = [
        "VERSION",
        "TITLE",
        "ARTIST",
        "MP3",
        "BPM",
    ]
    optional_attributes = [
        "GAP",
        "COVER",
        "BACKGROUND",
        "VIDEO",
        "VIDEOGAP",
        "GENRE",
        "EDITION",
        "CREATOR",
        "LANGUAGE",
        "YEAR",
        "START",
        "END",
        "PREVIEWSTART",
        "MEDLEYSTARTBEAT",
        "MEDLEYENDBEAT",
        "CALCMEDLEY",
        "DUETSINGERP1",
        "DUETSINGERP2",
        "P1",
        "P2",
        "COMMENT",
        "RESOLUTION",
        "NOTESGAP",
        "RELATIVE",
        "ENCODING",
    ]
    attribute_mappings = {}

    primary_audio_attributes = ["MP3"]


class UltrastarVersion100(BaseUltrastarVersion):
    _version: FormatVersion = FormatVersion("1.0.0")
    required_attributes = [
        "VERSION",
        "TITLE",
        "ARTIST",
        "MP3",
        "BPM",
    ]
    optional_attributes = [
        "GAP",
        "COVER",
        "BACKGROUND",
        "VIDEO",
        "VIDEOGAP",
        "GENRE",
        "EDITION",
        "CREATOR",
        "LANGUAGE",
        "YEAR",
        "START",
        "END",
        "PREVIEWSTART",
        "MEDLEYSTARTBEAT",
        "MEDLEYENDBEAT",
        "CALCMEDLEY",
        "P1",
        "P2",
        "COMMENT",
    ]
    attribute_mappings = {}

    primary_audio_attributes = ["MP3"]


class UltrastarVersion110(BaseUltrastarVersion):
    _version: FormatVersion = FormatVersion("1.1.0")
    required_attributes = [
        "VERSION",
        "TITLE",
        "ARTIST",
        "MP3",
        "AUDIO",
        "BPM",
    ]
    optional_attributes = [
        "VOCALS",
        "INSTRUMENTAL",
        "GAP",
        "COVER",
        "BACKGROUND",
        "VIDEO",
        "VIDEOGAP",
        "GENRE",
        "EDITION",
        "TAGS",
        "CREATOR",
        "LANGUAGE",
        "YEAR",
        "START",
        "END",
        "PREVIEWSTART",
        "MEDLEYSTARTBEAT",
        "MEDLEYENDBEAT",
        "CALCMEDLEY",
        "P1",
        "P2",
        "COMMENT",
        "PROVIDEDBY",
    ]
    attribute_mappings = {
        "upgrade": {
            "MP3": AttributeMapping(new_name="AUDIO", transform=None),
        },
        "downgrade": {
            "AUDIO": AttributeMapping(new_name="MP3", transform=None),
        },
    }

    primary_audio_attributes = ["MP3", "AUDIO"]


class UltrastarVersion120(BaseUltrastarVersion):
    _version: FormatVersion = FormatVersion("1.1.0")
    required_attributes = [
        "VERSION",
        "TITLE",
        "ARTIST",
        "MP3",
        "AUDIO",
        "BPM",
    ]
    optional_attributes = [
        "AUDIOURL",
        "VOCALS",
        "INSTRUMENTAL",
        "GAP",
        "COVER",
        "COVERURL",
        "BACKGROUND",
        "BACKGROUNDURL",
        "VIDEO",
        "VIDEOURL",
        "VIDEOGAP",
        "GENRE",
        "EDITION",
        "TAGS",
        "CREATOR",
        "LANGUAGE",
        "YEAR",
        "START",
        "END",
        "PREVIEWSTART",
        "MEDLEYSTARTBEAT",
        "MEDLEYENDBEAT",
        "CALCMEDLEY",
        "P1",
        "P2",
        "COMMENT",
        "PROVIDEDBY",
    ]
    attribute_mappings = {
        "upgrade": {
            "MP3": AttributeMapping(new_name="AUDIO", transform=None),
        },
        "downgrade": {
            "AUDIO": AttributeMapping(new_name="MP3", transform=None),
        },
    }

    primary_audio_attributes = ["MP3", "AUDIO"]


class UltrastarVersion200(BaseUltrastarVersion):
    _version: FormatVersion = FormatVersion("2.0.0")
    required_attributes = [
        "VERSION",
        "TITLE",
        "ARTIST",
        "AUDIO",
        "BPM",
    ]
    optional_attributes = [
        "GAP",
        "COVER",
        "BACKGROUND",
        "VIDEO",
        "VIDEOGAP",
        "GENRE",
        "EDITION",
        "CREATOR",
        "LANGUAGE",
        "YEAR",
        "START",
        "END",
        "PREVIEWSTART",
        "MEDLEYSTARTBEAT",
        "MEDLEYENDBEAT",
        "CALCMEDLEY",
        "P1",
        "P2",
        "COMMENT",
    ]
    attribute_mappings = {
        "upgrade": {
            "MP3": AttributeMapping(new_name="AUDIO", transform=None),
            "MEDLEYSTARTBEAT": AttributeMapping(
                new_name="MEDLEYSTART",
                transform=None,  # FIXME: transform
            ),
            "MEDLEYENDBEAT": AttributeMapping(
                new_name="MEDLEYEND",
                transform=None,  # FIXME: transform
            ),
        },
        "downgrade": {
            "AUDIO": AttributeMapping(new_name="MP3", transform=None),
            "MEDLEYSTART": AttributeMapping(new_name="MEDLEYSTARTBEAT", transform=None),
            "MEDLEYEND": AttributeMapping(new_name="MEDLEYENDBEAT", transform=None),
        },
    }

    primary_audio_attributes = ["MP3", "AUDIO"]


versions: dict[FormatVersion, BaseUltrastarVersion] = {
    FormatVersion("0.1.0"): UltrastarVersion010,
    FormatVersion("0.2.0"): UltrastarVersion020,
    FormatVersion("0.3.0"): UltrastarVersion030,
    FormatVersion("1.0.0"): UltrastarVersion100,
    FormatVersion("1.1.0"): UltrastarVersion110,
    FormatVersion("1.2.0"): UltrastarVersion120,
    FormatVersion("2.0.0"): UltrastarVersion200,
}
"""
Contains all supported Ultrastar file versions
"""


def _detect_version(attributes: dict[str, str]) -> FormatVersion:
    """
    Detects the Ultrastar file version based on the attributes present in the file.

    :param attributes: The attributes dict
    :return: The detected version
    """
    # Check if the version is explicitly defined. If so, and we support it, return it.
    if "VERSION" in attributes:
        version = FormatVersion(attributes["VERSION"])
        if version in versions.keys():
            return version

    best_version: FormatVersion = None
    max_optional_matches = -1

    for version_key in sorted(versions.keys(), reverse=True):
        version_class = versions.get(version_key)
        required_attrs = version_class.required_attributes
        optional_attrs = version_class.optional_attributes

        # Check if all required attributes are present
        if all(attr in attributes for attr in required_attrs):
            # Count matching optional attributes
            optional_matches = sum(1 for attr in optional_attrs if attr in attributes)

            # Select the version with the highest number of optional matches
            if optional_matches > max_optional_matches or (
                optional_matches == max_optional_matches
                and (best_version is None or version_key > best_version)
            ):
                best_version = version_key
                max_optional_matches = optional_matches

    if best_version is not None:
        return best_version

    # If no version was found, default to 1.0.0. This could be dangerous when upgrading/downgrading,
    # but we want to avoid crashing under any circumstances.
    return FormatVersion("1.0.0")


def ultrastar_version_factory(file: str) -> BaseUltrastarVersion:
    """
    Find a version for the Ultrastar file and return an instance of the corresponding class. If no version is found,
    return an instance of the 1.0.0 version.

    :param file: The Ultrastar file content. Not the file path.
    :return: An instance of the correct Ultrastar version class
    """
    attributes = {}
    lines = file.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            key, value = line[1:].split(":", 1)
            key = key.upper()
            attributes[key.strip()] = value.strip()
        elif line != "":
            break
    version = _detect_version(attributes)
    return versions.get(version)()
