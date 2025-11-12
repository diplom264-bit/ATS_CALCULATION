"""Synonym Mapping for Common Technical Terms"""

SYNONYM_MAP = {
    "asp.net": ["asp.net core", "asp.net mvc", "asp.net web api", "aspnet", "asp net"],
    "angular": ["angularjs", "angular 2", "angular 4", "angular 6", "angular 7", "angular 8", "angular 9"],
    "c#": ["c sharp", "csharp", "c-sharp"],
    "sql": ["sql server", "t-sql", "tsql", "structured query language"],
    ".net": ["dotnet", "dot net", ".net framework", ".net core"],
    "javascript": ["js", "ecmascript", "es6", "es2015"],
    "typescript": ["ts"],
    "power bi": ["powerbi", "power-bi"],
    "azure": ["microsoft azure", "azure cloud"],
    "aws": ["amazon web services"],
    "rest api": ["restful api", "rest web services", "restful"],
    "entity framework": ["ef", "ef core", "entity-framework"],
    "linq": ["language integrated query"],
    "ajax": ["asynchronous javascript"],
    "oracle": ["oracle database", "oracle db"]
}

def synonym_expand(term):
    """
    Expand a term to include all known synonyms.
    Returns list of terms to try for matching.
    """
    term_l = term.lower().strip()
    results = [term]
    
    # Check if term matches any key or value
    for key, vals in SYNONYM_MAP.items():
        if key == term_l or term_l in vals:
            results.append(key)
            results.extend(vals)
        elif key in term_l or any(v in term_l for v in vals):
            results.append(key)
            results.extend(vals)
    
    return list(set(results))
