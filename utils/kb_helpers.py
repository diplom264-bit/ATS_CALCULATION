"""KB Helper Functions - Normalization and Utilities"""

def normalize_skill_inputs(skills_raw):
    """
    Accepts list of skill strings or dicts and returns normalized list of strings.
    Handles None, dicts with various key names, and plain strings.
    """
    normalized = []
    for s in skills_raw:
        if s is None:
            continue
        if isinstance(s, dict):
            lbl = s.get("label") or s.get("name") or s.get("skill") or ""
            normalized.append(lbl.strip())
        else:
            normalized.append(str(s).strip())
    return [s for s in normalized if s]
