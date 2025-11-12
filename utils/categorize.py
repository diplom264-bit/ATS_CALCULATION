"""Skill Categorization - Enhanced Technical Detection"""

TECH_KEYWORDS = {
    "programming": ["programming", "development", "software", "coding", "engineer"],
    "web": ["asp", "asp.net", ".net", "dotnet", "angular", "react", "vue", "html", "css", 
            "javascript", "typescript", "ajax", "jquery", "bootstrap"],
    "db": ["sql", "oracle", "mysql", "postgres", "mongodb", "db", "database", "query", 
           "dax", "linq", "t-sql", "nosql", "redis"],
    "devops": ["ci/cd", "docker", "kubernetes", "azure", "aws", "gcp", "jenkins", 
               "gitlab", "devops", "terraform", "ansible"],
    "bi": ["power bi", "business intelligence", "tableau", "qlik", "reporting", 
           "analytics", "data warehouse", "etl"],
    "languages": ["python", "java", "c#", "csharp", "javascript", "typescript", "go", 
                  "rust", "kotlin", "swift", "php", "ruby"],
    "frameworks": ["framework", "library", "api", "rest", "graphql", "soap", "mvc", 
                   "webapi", "entity framework"],
    "data": ["data engineering", "data science", "machine learning", "ml", "ai", 
             "big data", "spark", "hadoop"]
}

OPERATIONAL_KEYWORDS = ["maintain", "support", "provide", "training", "troubleshoot", 
                        "deploy", "configure", "install", "monitor"]

def categorize_skill(skill_label):
    """
    Categorize skill as technical, operational, or domain.
    Enhanced with comprehensive keyword matching.
    """
    s = skill_label.lower()
    
    # Check technical keywords
    for cat, kw_list in TECH_KEYWORDS.items():
        for kw in kw_list:
            if kw in s:
                return "technical"
    
    # Check operational keywords
    if any(w in s for w in OPERATIONAL_KEYWORDS):
        return "operational"
    
    return "domain"
