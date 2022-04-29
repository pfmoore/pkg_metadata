from pkg_metadata import json_to_msg, msg_to_json, pyproject_to_json
from email import message_from_bytes, message_from_string

sample = {
    "metadata_version": "2.2",
    "name": "foo",
    "version": "1.0",
    "description": "Hello, world",
    "keywords": ["foo", "bar", "baz"],
    "requires_dist": ["pip", "tox"],
}

def test_roundtrip():
    m = json_to_msg(sample)
    j = msg_to_json(message_from_string(m))
    assert j == sample

def test_binary_utf8_msg():
    txt_msg = [
        "Name: test",
        "Version: 0.1",
        "Description: Un éxample, garçon!"
    ]
    bin_msg = "\n".join(txt_msg).encode("utf-8")
    j = msg_to_json(message_from_bytes(bin_msg))
    assert j["name"] == "test"
    assert j["version"] == "0.1"
    assert j["description"] == "Un éxample, garçon!"

def test_binary_latin1_msg():
    txt_msg = [
        "Name: test",
        "Version: 0.1",
        "Description: Un éxample, garçon!"
    ]
    bin_msg = "\n".join(txt_msg).encode("latin1")
    j = msg_to_json(message_from_bytes(bin_msg))
    assert j["name"] == "test"
    assert j["version"] == "0.1"
    assert j["description"] == "Un éxample, garçon!"

def test_keywords():
    msg = [
        "Name: test",
        "Version: 0.1",
        "Keywords: one two three"
    ]
    j = msg_to_json(message_from_string("\n".join(msg)))
    assert j["name"] == "test"
    assert j["version"] == "0.1"
    assert j["keywords"] == ["one", "two", "three"]

def test_pyproject():
    pyproject = {
        "name": "test",
        "version": "0.1",
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
    # TODO: optional-dependencies but no dependencies
    # TODO: readme
