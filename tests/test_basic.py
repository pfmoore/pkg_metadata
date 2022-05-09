from pkg_metadata import json_to_bytes, bytes_to_json, msg_to_json, pyproject_to_json
from email import message_from_bytes, message_from_string

import pytest

sample = {
    "metadata_version": "2.2",
    "name": "foo",
    "version": "1.0",
    "description": "Hello, world",
    "keywords": ["foo", "bar", "baz"],
    "requires_dist": ["pip", "tox"],
}


def test_roundtrip():
    m = json_to_bytes(sample)
    j = bytes_to_json(m)
    assert j == sample


def test_binary_utf8_msg():
    txt_msg = ["Name: test", "Version: 0.1", "Description: Un éxample, garçon!"]
    bin_msg = "\n".join(txt_msg).encode("utf-8")
    j = bytes_to_json(bin_msg)
    assert j["name"] == "test"
    assert j["version"] == "0.1"
    assert j["description"] == "Un éxample, garçon!"


def test_binary_latin1_msg():
    txt_msg = ["Name: test", "Version: 0.1", "Description: Un éxample, garçon!"]
    bin_msg = "\n".join(txt_msg).encode("latin1")
    j = bytes_to_json(bin_msg)
    assert j["name"] == "test"
    assert j["version"] == "0.1"
    assert j["description"] == "Un éxample, garçon!"


def test_keywords():
    msg = ["Name: test", "Version: 0.1", "Keywords: one two three"]
    j = msg_to_json(message_from_string("\n".join(msg)))
    assert j["name"] == "test"
    assert j["version"] == "0.1"
    assert j["keywords"] == ["one", "two", "three"]


def test_pyproject():
    pyproject = {
        "name": "test",
        "version": "0.1",
        "readme": {
            "text": "Example readme",
            "content-type": "text/plain",
        },
        "authors": [
            {"name": "Paul Moore", "email": "p.f.moore@gmail.com"},
            {"name": "Mickey Mouse"},
            {"name": "Snoopy"},
            {"email": "dummy@example.com"},
            {},
        ],
        "urls": {"Home": "https://github.com"},
        "dependencies": ["pip", "rich"],
        "optional-dependencies": {
            "test": [
                "pytest",
                "xxx; os_name == 'nt'",
            ],
        },
    }
    j = pyproject_to_json(pyproject)
    assert j["name"] == "test"
    assert j["version"] == "0.1"
    assert j["description"] == "Example readme"
    assert j["description_content_type"] == "text/plain"
    # Note core metadata spec - these are *not* multi-use!
    assert j["author"] == "Mickey Mouse, Snoopy"
    assert j["author_email"] == "Paul Moore <p.f.moore@gmail.com>, dummy@example.com"
    assert j["project_url"] == ["Home: https://github.com"]
    assert j["provides_extra"] == ["test"]
    # TODO: Maybe test requirements using packaging, if that
    #       handles cosmetic differences better...
    assert j["requires_dist"] == [
        "pip",
        "rich",
        'pytest; extra == "test"',
        'xxx; os_name == "nt" and extra == "test"',
    ]


def test_pyproject_optional_deps_only():
    pyproject = {
        "name": "test",
        "version": "0.1",
        "optional-dependencies": {
            "test": [
                "pytest",
                "xxx; os_name == 'nt'",
            ],
        },
    }
    j = pyproject_to_json(pyproject)
    assert j["name"] == "test"
    assert j["version"] == "0.1"
    assert j["provides_extra"] == ["test"]
    assert j["requires_dist"] == [
        'pytest; extra == "test"',
        'xxx; os_name == "nt" and extra == "test"',
    ]


@pytest.mark.parametrize(
    "name,content_type",
    [
        ("README.md", "text/markdown"),
        ("README.rst", "text/x-rst"),
    ],
)
def test_pyproject_readme_file(name, content_type, tmp_path):
    (tmp_path / name).write_text("Example")
    j = pyproject_to_json(
        {"name": "foo", "version": "1.0", "readme": str(tmp_path / name)}
    )
    assert j["description"] == "Example"
    assert j["description_content_type"] == content_type


@pytest.mark.parametrize(
    "name,content_type",
    [
        ("README.md", "text/plain"),
        ("README.rst", "text/plain"),
        ("README", "text/markdown"),
    ],
)
def test_pyproject_readme_explicit_file(name, content_type, tmp_path):
    (tmp_path / name).write_text("Example")
    j = pyproject_to_json(
        {
            "name": "foo",
            "version": "1.0",
            "readme": {"file": str(tmp_path / name), "content-type": content_type},
        }
    )
    assert j["description"] == "Example"
    assert j["description_content_type"] == content_type


@pytest.mark.parametrize("encoding", ["utf-8", "latin1"])
def test_pyproject_readme_encoding(encoding, tmp_path):
    (tmp_path / "README").write_text("Éxample", encoding=encoding)
    j = pyproject_to_json(
        {
            "name": "foo",
            "version": "1.0",
            "readme": {
                "file": str(tmp_path / "README"),
                "content-type": "text/plain",
                "charset": encoding,
            },
        }
    )
    assert j["description"] == "Éxample"


def test_pytest_readme_no_type(tmp_path):
    (tmp_path / "README.md").write_text("Example")
    with pytest.raises(ValueError) as exc:
        pyproject_to_json(
            {
                "name": "foo",
                "version": "1.0",
                "readme": {"file": str(tmp_path / "README.md")},
            }
        )
    assert "no content type" in str(exc.value)


def test_pytest_readme_text_and_file(tmp_path):
    (tmp_path / "README.md").write_text("Example")
    with pytest.raises(ValueError) as exc:
        pyproject_to_json(
            {
                "name": "foo",
                "version": "1.0",
                "readme": {
                    "file": str(tmp_path / "README.md"),
                    "text": "Example",
                    "content-type": "text/plain",
                },
            }
        )
    assert "mutually exclusive" in str(exc.value)
