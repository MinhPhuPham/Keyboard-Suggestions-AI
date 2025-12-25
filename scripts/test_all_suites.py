#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
Tests all Japanese IME functionality with enhanced engine
"""

import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.append('scripts')

from enhanced_predictive_engine import EnhancedJapanesePredictiveEngine

class ComprehensiveTestRunner:
    """Run all Japanese IME tests"""
    
    def __init__(self):
        self.engine = EnhancedJapanesePredictiveEngine()
        self.results = {
            'test_kanji_cases': {'passed': 0, 'failed': 0, 'total': 0},
            'test_kanji_v2_cases': {'passed': 0, 'failed': 0, 'total': 0, 'context_passed': 0, 'context_total': 0}
        }
    
    def run_test_kanji_cases(self):
        """Run test-kanji-cases.json (original predictive text tests)"""
        print("\n" + "="*70)
        print("TEST SUITE 1: Predictive Text (test-kanji-cases.json)")
        print("="*70)
        
        test_file = Path('test-data/test-kanji-cases.json')
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = data.get('test_categories', [])
        total_passed = 0
        total_tests = 0
        
        for category in categories:
            category_name = category.get('category', 'Unknown')
            tests = category.get('tests', [])
            
            print(f"\n{category_name}:")
            
            for test in tests:
                total_tests += 1
                input_text = test.get('input', '')
                expected = test.get('expected_suggestions', [])
                
                # Get predictions
                predictions = self.engine.get_predictions(input_text)
                
                # Check if any expected is in predictions
                passed = any(exp in predictions for exp in expected)
                
                if passed:
                    total_passed += 1
                    print(f"  ✅ {input_text} → {predictions[:3]}")
                else:
                    print(f"  ❌ {input_text} → Expected: {expected[:3]}, Got: {predictions[:3]}")
        
        self.results['test_kanji_cases']['passed'] = total_passed
        self.results['test_kanji_cases']['failed'] = total_tests - total_passed
        self.results['test_kanji_cases']['total'] = total_tests
        
        percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\n{'='*70}")
        print(f"Result: {total_passed}/{total_tests} passed ({percentage:.1f}%)")
        print("="*70)
        
        return percentage >= 95
    
    def run_test_kanji_v2_cases(self):
        """Run test-kanji-v2-cases.json (advanced context tests)"""
        print("\n" + "="*70)
        print("TEST SUITE 2: Advanced Context-Aware (test-kanji-v2-cases.json)")
        print("="*70)
        
        test_file = Path('test-data/test-kanji-v2-cases.json')
        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = data.get('test_categories', [])
        total_passed = 0
        total_tests = 0
        context_passed = 0
        context_total = 0
        
        for category in categories:
            category_name = category.get('category', 'Unknown')
            tests = category.get('tests', [])
            
            print(f"\n{category_name}:")
            
            for test in tests:
                total_tests += 1
                input_text = test.get('input', '')
                expected = test.get('expected_suggestions_default', test.get('expected_suggestions', []))
                
                # Basic test
                predictions = self.engine.get_predictions(input_text)
                passed = any(exp in predictions for exp in expected)
                
                if passed:
                    total_passed += 1
                    status = "✅"
                else:
                    status = "❌"
                
                print(f"  {status} {input_text} → {predictions[:3]}")
                
                # Context tests
                context_vars = test.get('context_variations', [])
                if context_vars:
                    ctx_pass = 0
                    ctx_total = len(context_vars)
                    context_total += ctx_total
                    
                    for ctx in context_vars:
                        context_str = ctx.get('context', '')
                        expected_priority = ctx.get('expected_priority', [])
                        
                        # Parse context
                        context_dict = self.parse_context_string(context_str)
                        
                        # Get predictions with context
                        ctx_predictions = self.engine.get_predictions(input_text, context_dict)
                        
                        # Check if top expected matches
                        if expected_priority and len(ctx_predictions) > 0:
                            if expected_priority[0] == ctx_predictions[0]:
                                ctx_pass += 1
                                context_passed += 1
                    
                    if ctx_total > 0:
                        print(f"     Context: {ctx_pass}/{ctx_total}")
        
        self.results['test_kanji_v2_cases']['passed'] = total_passed
        self.results['test_kanji_v2_cases']['failed'] = total_tests - total_passed
        self.results['test_kanji_v2_cases']['total'] = total_tests
        self.results['test_kanji_v2_cases']['context_passed'] = context_passed
        self.results['test_kanji_v2_cases']['context_total'] = context_total
        
        percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
        context_percentage = (context_passed / context_total * 100) if context_total > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"Basic: {total_passed}/{total_tests} passed ({percentage:.1f}%)")
        print(f"Context: {context_passed}/{context_total} passed ({context_percentage:.1f}%)")
        print("="*70)
        
        return percentage >= 95 and context_percentage >= 60
    
    def parse_context_string(self, context_str: str) -> dict:
        """Parse context string"""
        context = {}
        
        if 'preceding_text:' in context_str:
            start = context_str.find("'") + 1
            end = context_str.rfind("'")
            if start > 0 and end > start:
                context['preceding_text'] = context_str[start:end]
        
        if 'following_text:' in context_str:
            start = context_str.find("'") + 1
            end = context_str.rfind("'")
            if start > 0 and end > start:
                context['following_text'] = context_str[start:end]
        
        if 'sentence_start: true' in context_str:
            context['sentence_start'] = True
        
        return context
    
    def print_final_summary(self):
        """Print comprehensive summary"""
        print("\n" + "="*70)
        print("COMPREHENSIVE TEST SUMMARY")
        print("="*70)
        
        # Test Suite 1
        suite1 = self.results['test_kanji_cases']
        suite1_pct = (suite1['passed'] / suite1['total'] * 100) if suite1['total'] > 0 else 0
        
        print(f"\n📊 Test Suite 1: Predictive Text")
        print(f"   {suite1['passed']}/{suite1['total']} passed ({suite1_pct:.1f}%)")
        
        # Test Suite 2
        suite2 = self.results['test_kanji_v2_cases']
        suite2_pct = (suite2['passed'] / suite2['total'] * 100) if suite2['total'] > 0 else 0
        suite2_ctx_pct = (suite2['context_passed'] / suite2['context_total'] * 100) if suite2['context_total'] > 0 else 0
        
        print(f"\n📊 Test Suite 2: Advanced Context-Aware")
        print(f"   Basic: {suite2['passed']}/{suite2['total']} passed ({suite2_pct:.1f}%)")
        print(f"   Context: {suite2['context_passed']}/{suite2['context_total']} passed ({suite2_ctx_pct:.1f}%)")
        
        # Overall
        total_tests = suite1['total'] + suite2['total']
        total_passed = suite1['passed'] + suite2['passed']
        overall_pct = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 Overall Performance")
        print(f"   Total: {total_passed}/{total_tests} passed ({overall_pct:.1f}%)")
        print(f"   Context Accuracy: {suite2_ctx_pct:.1f}%")
        
        print(f"\n{'='*70}")
        print("PRODUCTION STATUS")
        print(f"{'='*70}")
        
        if suite1_pct >= 95 and suite2_pct >= 95 and suite2_ctx_pct >= 60:
            print("✅ EXCELLENT - PRODUCTION READY!")
            print("   - All test suites passing")
            print("   - Context awareness working well")
            print("   - Ready for deployment")
        elif suite1_pct >= 90 and suite2_pct >= 90:
            print("✅ GOOD - PRODUCTION READY")
            print("   - Core functionality excellent")
            print("   - Minor improvements possible")
        else:
            print("⚠️  NEEDS IMPROVEMENT")
            print("   - Some tests failing")
            print("   - Review failed cases")
        
        print("="*70)
        
        # Save results
        results_file = Path('test-data/comprehensive-test-results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Results saved to: {results_file}")
        print("="*70)


def main():
    print("\n" + "="*70)
    print("COMPREHENSIVE JAPANESE IME TEST SUITE")
    print("="*70)
    print("\n🎯 Testing enhanced prediction engine against all test cases")
    print("📁 Test files:")
    print("   1. test-data/test-kanji-cases.json (Predictive Text)")
    print("   2. test-data/test-kanji-v2-cases.json (Advanced Context)")
    print("="*70)
    
    runner = ComprehensiveTestRunner()
    
    # Run tests
    suite1_pass = runner.run_test_kanji_cases()
    suite2_pass = runner.run_test_kanji_v2_cases()
    
    # Print summary
    runner.print_final_summary()
    
    # Exit code
    sys.exit(0 if (suite1_pass and suite2_pass) else 1)


if __name__ == '__main__':
    main()
