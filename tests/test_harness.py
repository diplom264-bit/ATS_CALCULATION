"""Test Harness for Resume Parser - Batch Testing"""
import sys
sys.path.insert(0, 'D:/ATSsys/version_4')

from app.services.final_resume_parser import FinalResumeParser
from pathlib import Path

class TestHarness:
    """Batch test multiple resumes and track metrics"""
    
    def __init__(self):
        self.parser = FinalResumeParser()
        self.results = []
    
    def test_resume(self, file_path: str, expected: dict = None) -> dict:
        """Test single resume and return metrics"""
        result = self.parser.parse(file_path)
        
        if result['status'] != 'ok':
            return {'file': file_path, 'status': 'error', 'error': result.get('error')}
        
        # Calculate metrics
        metrics = {
            'file': Path(file_path).name,
            'status': 'ok',
            'extracted': {
                'name': bool(result['name']),
                'email': bool(result['email']),
                'phone': bool(result['phone']),
                'skills': len(result['skills']),
                'companies': len(result['companies']),
                'titles': len(result['job_titles']),
                'degrees': len(result['degrees'])
            },
            'score': self._calculate_score(result)
        }
        
        # Compare with expected if provided
        if expected:
            metrics['accuracy'] = self._calculate_accuracy(result, expected)
        
        self.results.append(metrics)
        return metrics
    
    def _calculate_score(self, result: dict) -> float:
        """Calculate extraction score (0-1)"""
        fields = [
            bool(result['name']),
            bool(result['email']),
            bool(result['phone']),
            bool(result['skills']),
            bool(result['companies']),
            bool(result['degrees'])
        ]
        return sum(fields) / len(fields)
    
    def _calculate_accuracy(self, result: dict, expected: dict) -> dict:
        """Calculate accuracy against expected values"""
        accuracy = {}
        
        if 'name' in expected:
            accuracy['name'] = result['name'] == expected['name']
        
        if 'email' in expected:
            accuracy['email'] = result['email'] == expected['email']
        
        if 'skills' in expected:
            extracted = set(s.lower() for s in result['skills'])
            expected_set = set(s.lower() for s in expected['skills'])
            if expected_set:
                accuracy['skills_recall'] = len(extracted & expected_set) / len(expected_set)
        
        return accuracy
    
    def test_batch(self, resume_paths: list) -> dict:
        """Test multiple resumes and return summary"""
        print(f"Testing {len(resume_paths)} resumes...\n")
        
        for path in resume_paths:
            print(f"Testing: {Path(path).name}")
            metrics = self.test_resume(path)
            
            if metrics['status'] == 'ok':
                print(f"  Score: {metrics['score']:.0%}")
                print(f"  Extracted: {metrics['extracted']}")
            else:
                print(f"  ❌ Error: {metrics.get('error')}")
            print()
        
        return self.get_summary()
    
    def get_summary(self) -> dict:
        """Get summary statistics"""
        if not self.results:
            return {}
        
        ok_results = [r for r in self.results if r['status'] == 'ok']
        
        if not ok_results:
            return {'total': len(self.results), 'errors': len(self.results)}
        
        avg_score = sum(r['score'] for r in ok_results) / len(ok_results)
        
        # Field-level stats
        field_stats = {
            'name': sum(1 for r in ok_results if r['extracted']['name']) / len(ok_results),
            'email': sum(1 for r in ok_results if r['extracted']['email']) / len(ok_results),
            'phone': sum(1 for r in ok_results if r['extracted']['phone']) / len(ok_results),
            'skills': sum(1 for r in ok_results if r['extracted']['skills'] > 0) / len(ok_results),
            'companies': sum(1 for r in ok_results if r['extracted']['companies'] > 0) / len(ok_results),
            'degrees': sum(1 for r in ok_results if r['extracted']['degrees'] > 0) / len(ok_results)
        }
        
        return {
            'total': len(self.results),
            'successful': len(ok_results),
            'errors': len(self.results) - len(ok_results),
            'avg_score': avg_score,
            'field_accuracy': field_stats
        }
    
    def print_summary(self):
        """Print formatted summary"""
        summary = self.get_summary()
        
        print("="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"\nTotal Resumes: {summary['total']}")
        print(f"Successful: {summary['successful']}")
        print(f"Errors: {summary['errors']}")
        print(f"\nAverage Score: {summary['avg_score']:.1%}")
        
        print(f"\nField Extraction Rates:")
        for field, rate in summary['field_accuracy'].items():
            status = "✅" if rate >= 0.9 else "⚠️" if rate >= 0.7 else "❌"
            print(f"  {status} {field}: {rate:.0%}")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    harness = TestHarness()
    
    # Test current resumes
    resumes = [
        r"C:\Users\Owner\Downloads\RitikSharma_BI Developer.pdf",
        r"C:\Users\Owner\Downloads\Nakul_Saraswat_Resume 1 (1).pdf"
    ]
    
    harness.test_batch(resumes)
    harness.print_summary()
