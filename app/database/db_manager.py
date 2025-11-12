"""
Database Manager - SQLite for JD and Resume storage
"""
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional

class DatabaseManager:
    """Manage JD and Resume storage"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent / "ats.db")
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables with session tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # JD table with session_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                title TEXT,
                company TEXT,
                location TEXT,
                job_type TEXT,
                description TEXT,
                responsibilities TEXT,
                qualifications TEXT,
                education TEXT,
                benefits TEXT,
                must_have TEXT,
                nice_to_have TEXT,
                min_experience_years INTEGER,
                text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Resume table with session_id and jd_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id TEXT PRIMARY KEY,
                jd_id TEXT,
                session_id TEXT,
                name TEXT,
                email TEXT,
                phone TEXT,
                skills TEXT,
                experience_years INTEGER,
                roles TEXT,
                education TEXT,
                text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (jd_id) REFERENCES job_descriptions(id) ON DELETE CASCADE
            )
        """)
        
        # Match results table with session_id and CASCADE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS match_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jd_id TEXT,
                resume_id TEXT,
                session_id TEXT,
                match_score REAL,
                grade TEXT,
                match_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (jd_id) REFERENCES job_descriptions(id) ON DELETE CASCADE,
                FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE
            )
        """)
        
        # Add session_id columns if they don't exist (migration)
        try:
            cursor.execute("ALTER TABLE job_descriptions ADD COLUMN session_id TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE resumes ADD COLUMN session_id TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE resumes ADD COLUMN jd_id TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE match_results ADD COLUMN session_id TEXT")
        except:
            pass
        
        conn.commit()
        conn.close()
    
    def save_jd(self, jd: Dict) -> bool:
        """Save job description with session_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO job_descriptions 
            (id, session_id, title, company, location, job_type, description, responsibilities, 
             qualifications, education, benefits, must_have, nice_to_have, min_experience_years, text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            jd['jd_id'],
            jd.get('session_id'),
            jd.get('title', 'Job Opening'),
            jd.get('company', ''),
            jd.get('location', ''),
            jd.get('job_type', 'Full-time'),
            jd.get('description', ''),
            json.dumps(jd.get('responsibilities', [])),
            json.dumps(jd.get('qualifications', [])),
            jd.get('education', ''),
            json.dumps(jd.get('benefits', [])),
            json.dumps(jd.get('must_have', [])),
            json.dumps(jd.get('nice_to_have', [])),
            jd.get('min_experience_years', 0),
            jd.get('text', '')
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def get_jd(self, jd_id: str) -> Optional[Dict]:
        """Get job description"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM job_descriptions WHERE id = ?", (jd_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'jd_id': row['id'],
            'session_id': row['session_id'],
            'title': row['title'],
            'text': row['text']
        }
    
    def list_jds(self) -> List[Dict]:
        """List all JDs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, created_at FROM job_descriptions ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [{'id': r[0], 'title': r[1], 'created_at': r[2]} for r in rows]
    
    def save_resume(self, resume: Dict) -> bool:
        """Save resume with jd_id and session_id - check for duplicates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if resume already exists in this session
        email = resume.get('email', '')
        session_id = resume.get('session_id')
        
        if email and session_id:
            cursor.execute("""
                SELECT id FROM resumes 
                WHERE email = ? AND session_id = ?
            """, (email, session_id))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing resume instead of creating duplicate
                cursor.execute("""
                    UPDATE resumes 
                    SET name=?, phone=?, skills=?, experience_years=?, roles=?, education=?, text=?
                    WHERE id=?
                """, (
                    resume.get('name', 'Unknown'),
                    resume.get('phone', ''),
                    json.dumps(resume.get('skills', [])),
                    resume.get('experience_years', 0),
                    json.dumps(resume.get('roles', [])),
                    json.dumps(resume.get('education', [])),
                    resume.get('text', ''),
                    existing[0]
                ))
                conn.commit()
                conn.close()
                return existing[0]  # Return existing ID
        
        # Insert new resume
        cursor.execute("""
            INSERT INTO resumes 
            (id, jd_id, session_id, name, email, phone, skills, experience_years, roles, education, text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resume['resume_id'],
            resume.get('jd_id'),
            resume.get('session_id'),
            resume.get('name', 'Unknown'),
            resume.get('email', ''),
            resume.get('phone', ''),
            json.dumps(resume.get('skills', [])),
            resume.get('experience_years', 0),
            json.dumps(resume.get('roles', [])),
            json.dumps(resume.get('education', [])),
            resume.get('text', '')
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def get_resume(self, resume_id: str) -> Optional[Dict]:
        """Get resume"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'resume_id': row['id'],
            'name': row['name'],
            'email': row['email'],
            'phone': row['phone'],
            'skills': json.loads(row['skills']) if row['skills'] else [],
            'experience_years': row['experience_years'],
            'roles': json.loads(row['roles']) if row['roles'] else [],
            'education': json.loads(row['education']) if row['education'] else [],
            'text': row['text']
        }
    
    def list_resumes(self) -> List[Dict]:
        """List all resumes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, email, created_at FROM resumes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [{'id': r[0], 'name': r[1], 'email': r[2], 'created_at': r[3]} for r in rows]
    
    def save_match(self, jd_id: str, resume_id: str, match_data: Dict) -> bool:
        """Save match result with session_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO match_results (jd_id, resume_id, session_id, match_score, grade, match_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            jd_id,
            resume_id,
            match_data.get('session_id'),
            match_data.get('match_score', 0),
            match_data.get('grade', 'F'),
            json.dumps(match_data)
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def get_batch_results(self, jd_id: str) -> List[Dict]:
        """Get all match results for a JD"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mr.*, r.name, r.email 
            FROM match_results mr
            JOIN resumes r ON mr.resume_id = r.id
            WHERE mr.jd_id = ?
            ORDER BY mr.match_score DESC
        """, (jd_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_batch_results_by_session(self, session_id: str) -> List[Dict]:
        """Get all match results for a session"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mr.*, r.name, r.email 
            FROM match_results mr
            JOIN resumes r ON mr.resume_id = r.id
            WHERE mr.session_id = ?
            ORDER BY mr.match_score DESC
        """, (session_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_resumes_by_jd(self, jd_id: str) -> List[Dict]:
        """Get all resumes for a JD"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM resumes WHERE jd_id = ? ORDER BY created_at DESC
        """, (jd_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
