import sqlite3, zlib, pkg_metadata
from email import message_from_bytes, message_from_string

def match(d1, d2):
    """Match ignoring whitespace differences in values"""
    assert d1.keys() == d2.keys(), f"{sorted(d1.keys())} vs {sorted(d2.keys())}"
    for k in d1:
        if isinstance(d1[k], list):
            v1 = [v.replace("\n","").replace(" ","") for v in d1[k]]
            v2 = [v.replace("\n","").replace(" ","") for v in d2[k]]
            assert v1 == v2, f"{k}: {d1[k]} vs {d2[k]}"
        else:
            assert d1[k].replace("\n", "").replace(" ", "") == d2[k].replace("\n", "").replace(" ", ""),  f"{k}: {d1[k]} vs {d2[k]}"

conn = sqlite3.connect(r"..\pypidata\Metadata.db")                      
for file, meta in conn.execute("select filename, metadata from project_metadata"):
    meta = zlib.decompress(meta)
    msg = message_from_bytes(meta)
    try:
        j = pkg_metadata.msg_to_json(msg)
        m = pkg_metadata.json_to_msg(j)
        j2 = pkg_metadata.msg_to_json(message_from_string(m))
        if j.get("description", "xxx") == "" and "description" not in j2:
            j2["description"] = ""
        match(j, j2)
    except Exception:
        print(file)
        print(meta)
        print(msg.as_string())
        raise
