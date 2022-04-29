from email.message import Message
from email.header import Header, make_header, decode_header
from pathlib import Path
from typing import Any, Union

from packaging.markers import Marker
from packaging.requirements import Requirement

METADATA_FIELDS = [
    # Name, Multiple-Use
    ("Metadata-Version", False),
    ("Name", False),
    ("Version", False),
    ("Dynamic", True),
    ("Platform", True),
    ("Supported-Platform", True),
    ("Summary", False),
    ("Description", False),
    ("Description-Content-Type", False),
    ("Keywords", False),
    ("Home-page", False),
    ("Download-URL", False),
    ("Author", False),
    ("Author-email", False),
    ("Maintainer", False),
    ("Maintainer-email", False),
    ("License", False),
    ("Classifier", True),
    ("Requires-Dist", True),
    ("Requires-Python", False),
    ("Requires-External", True),
    ("Project-URL", True),
    ("Provides-Extra", True),
    ("Provides-Dist", True),
    ("Obsoletes-Dist", True),
]


def json_name(field: str) -> str:
    return field.lower().replace("-", "_")


def msg_to_json(msg: Message) -> dict[str, Any]:
    def sanitise_header(h) -> str:
        if isinstance(h, Header):
            chunks = []
            for bytes, encoding in decode_header(h):
                if encoding == "unknown-8bit":
                    try:
                        # See if UTF-8 works
                        bytes.decode("utf-8")
                        encoding = "utf-8"
                    except UnicodeDecodeError:
                        # If not, latin1 at least won't fail
                        encoding = "latin1"
                chunks.append((bytes, encoding))
            return str(make_header(chunks))
        return str(h)

    result = {}
    for field, multi in METADATA_FIELDS:
        if field not in msg:
            continue
        key = json_name(field)
        if multi:
            value: Union[str, list[str]] = [
                sanitise_header(v) for v in msg.get_all(field)
            ]
        else:
            value = sanitise_header(msg.get(field))
            if key == "keywords":
                if "," in value:
                    value = [v.strip() for v in value.split(",")]
                else:
                    value = value.split()
        result[key] = value

    payload = msg.get_payload()
    if payload:
        result["description"] = payload

    return result


# Copied from distutils.util in Python 3.10
# NOTE: This doesn't preserve whitespace properly, but
#       it's the standard approach used by Python as far
#       as I can tell...
def rfc822_escape(header: str) -> str:
    """Return a version of the string escaped for inclusion in an
    RFC-822 header, by ensuring there are 8 spaces space after each newline.
    """
    lines = header.split("\n")
    sep = "\n" + 8 * " "
    return sep.join(lines)


def json_to_msg(metadata: dict[str, Any]) -> str:
    lines = []
    payload = None
    for field, multi in METADATA_FIELDS:
        key = json_name(field)
        value = metadata.get(key)
        if value is None:
            continue

        if key == "keywords":
            lines.append(f"{field}: {rfc822_escape(','.join(value))}")
        elif key == "description":
            payload = value
        elif multi:
            for val in value:
                lines.append(f"{field}: {rfc822_escape(val)}")
        else:
            lines.append(f"{field}: {rfc822_escape(value)}")

    msg = "\n".join(lines)
    if payload is not None:
        msg = msg + "\n\n" + payload

    return msg


def pyproject_to_json(pyproject: dict[str, Any]) -> dict[str, Any]:

    json_data: dict[str, Any] = {}
    json_data["metadata_version"] = None

    def copy_to(pyproject_name, json_name=None):
        if json_name is None:
            json_name = pyproject_name
        if pyproject_name in pyproject:
            json_data[json_name] = pyproject[pyproject_name]

    copy_to("name")
    copy_to("version")
    copy_to("description", "summary")
    copy_to("requires_python")
    copy_to("keywords")
    copy_to("classifiers", "classifier")
    copy_to("dependencies", "requires_dist")
    copy_to("dynamic")  # TODO: May need review

    def person_list(tag):
        email_list = []
        name_list = []
        for person in pyproject.get(f"{tag}s", []):
            name = person.get("name")
            email = person.get("email")
            if email is None:
                if name is None:
                    continue  # Warn?
                name_list.append(name)
            else:
                if name is None:
                    email_list.append(email)
                else:
                    email_list.append(f"{name} <{email}>")  # TODO: Quote properly!
        if name_list:
            json_data[tag] = ", ".join(name_list)
        if email_list:
            json_data[f"{tag}_email"] = ", ".join(email_list)

    person_list("author")
    person_list("maintainer")

    if "urls" in pyproject:
        json_data["project_url"] = [
            f"{label}: {url}" for label, url in pyproject["urls"].items()
        ]

    extras = []
    extra_deps = []
    for extra, deps in pyproject.get("optional-dependencies", {}).items():
        extras.append(extra)
        for dep in deps:
            req = Requirement(dep)
            if req.marker is None:
                req.marker = Marker(f"extra == '{extra}'")
            else:
                req.marker = Marker(f"({req.marker}) and extra == '{extra}'")
            extra_deps.append(str(req))

    if extras:
        json_data["provides_extra"] = extras
    if extra_deps:
        if "requires_dist" not in json_data:
            json_data["requires_dist"] = extra_deps
        else:
            json_data["requires_dist"].extend(extra_deps)

    if "readme" in pyproject:
        readme = pyproject["readme"]
        if isinstance(readme, str):
            content_type = None
            if readme.endswith(".md"):
                content_type = "text/markdown"
            elif readme.endswith(".rst"):
                content_type = "text/x-rst"
            readme = {"file": readme, "charset": "utf-8"}
            if content_type:
                readme["content-type"] = content_type
        if "content-type" not in readme:
            raise ValueError("readme: no content type specified")
        json_data["description_content_type"] = readme["content-type"]
        if "text" in readme:
            if "file" in readme:
                raise ValueError("readme: file and text are mutually exclusive")
            json_data["description"] = readme["text"]
        else:
            json_data["description"] = Path(readme["file"]).read_text(
                encoding=readme.get("charset", "utf-8")
            )

    # Incompletely specified.
    # The License core metadata examples and text suggest that it should be
    # a short, descriptive comment, not the full license text. But PEP 621
    # states that the "license" key provides the license *text* (either directly
    # or via a filename).
    # Currently, flit doesn't put the "license" key into the project metadata.
    # We will do the same for now.
    # json_data["license"] = None  # license

    # Covered by urls
    # json_data["home_page"] = None
    # json_data["download_url"] = None

    # Not in PEP 621
    # json_data["platform"] = None
    # json_data["supported_platform"] = None
    # json_data["requires_external"] = None
    # json_data["provides_dist"] = None
    # json_data["obsoletes_dist"] = None

    return json_data
