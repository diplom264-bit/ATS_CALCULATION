"""Quick test to verify keyword extraction works"""
from sklearn.feature_extraction.text import TfidfVectorizer

jd_text = """ATL .Net + Angular 6-8 yrs
Required Skills: .NET, Angular, C#, ASP.NET, SQL Server
Experience with web development and REST APIs"""

resume_text = """Anurag Kumar Srivastav
.NET Developer with 2.8 years experience
Skills: C#, Angular, ASP.NET Core, SQL Server, REST APIs
Worked on web applications using .NET framework"""

# Test TF-IDF extraction
vectorizer = TfidfVectorizer(stop_words='english', max_features=20, ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])

jd_vector = tfidf_matrix[0].toarray()[0]
feature_names = vectorizer.get_feature_names_out()
jd_keywords = [feature_names[i] for i in jd_vector.argsort()[-20:][::-1] if jd_vector[i] > 0]

print(f"JD Keywords: {jd_keywords}")

# Check matches
resume_lower = resume_text.lower()
found = [kw for kw in jd_keywords if kw in resume_lower]
missing = [kw for kw in jd_keywords if kw not in found]

print(f"\nMatched: {found}")
print(f"Missing: {missing}")
print(f"\nMatch rate: {len(found)}/{len(jd_keywords)} = {len(found)/len(jd_keywords)*100:.1f}%")
