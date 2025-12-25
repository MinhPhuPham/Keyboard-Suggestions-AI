#!/usr/bin/env python3
"""
Advanced Japanese Kanji Test Suite
Tests context-aware suggestions, homonyms, and learning behavior
"""

import json
from pathlib import Path
from typing import List, Dict, Any

class AdvancedKanjiTester:
    """Test advanced kanji suggestions with context awareness"""
    
    def __init__(self):
        self.test_file = Path('test-data/test-kanji-v2-cases.json')
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'categories': {}
        }
        
    def load_tests(self) -> Dict:
        """Load test cases"""
        with open(self.test_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_suggestions(self, hiragana: str, context: Dict = None) -> List[str]:
        """
        Get suggestions for hiragana input
        This is a simplified version - in production, this would use the actual model
        """
        # Import the predictive text dictionary
        import sys
        sys.path.append('scripts')
        from test_predictive_text import JapanesePredictiveTextDictionary
        
        dictionary = JapanesePredictiveTextDictionary()
        suggestions = dictionary.get_predictions(hiragana)
        
        # In a full implementation, context would influence ordering
        # For now, we return the basic suggestions
        return suggestions
    
    def test_basic_suggestions(self, test: Dict) -> bool:
        """Test basic suggestion without context"""
        input_text = test.get('input', '')
        expected = test.get('expected_suggestions_default', [])
        
        if not expected:
            expected = test.get('expected_suggestions', [])
        
        suggestions = self.get_suggestions(input_text)
        
        # Check if ANY expected suggestion is in our suggestions
        found = any(exp in suggestions for exp in expected)
        
        return found
    
    def test_context_variations(self, test: Dict) -> Dict:
        """Test context-aware suggestions"""
        results = {
            'total': 0,
            'passed': 0,
            'contexts': []
        }
        
        context_vars = test.get('context_variations', [])
        if not context_vars:
            return results
        
        for ctx in context_vars:
            results['total'] += 1
            expected_priority = ctx.get('expected_priority', [])
            
            # For now, we just check if the top expected is in our suggestions
            # Full implementation would check ordering
            suggestions = self.get_suggestions(test['input'])
            
            if expected_priority and expected_priority[0] in suggestions:
                results['passed'] += 1
                results['contexts'].append({
                    'context': ctx.get('context', ''),
                    'status': 'PASS'
                })
            else:
                results['contexts'].append({
                    'context': ctx.get('context', ''),
                    'status': 'FAIL',
                    'expected': expected_priority[0] if expected_priority else '',
                    'got': suggestions[:3]
                })
        
        return results
    
    def run_category_tests(self, category: Dict) -> Dict:
        """Run all tests in a category"""
        category_name = category.get('category', 'Unknown')
        tests = category.get('tests', [])
        
        print(f"\n{'='*70}")
        print(f"Testing: {category_name}")
        print(f"{'='*70}")
        
        passed = 0
        failed = 0
        details = []
        
        for test in tests:
            input_text = test.get('input', '')
            
            # Test basic suggestions
            basic_pass = self.test_basic_suggestions(test)
            
            if basic_pass:
                passed += 1
                status = "✅"
            else:
                failed += 1
                status = "❌"
            
            expected = test.get('expected_suggestions_default', test.get('expected_suggestions', []))
            suggestions = self.get_suggestions(input_text)
            
            print(f"\n{status} Input: '{input_text}'")
            print(f"   Expected: {expected[:5]}")
            print(f"   Got: {suggestions[:5]}")
            
            # Test context variations if present
            context_results = self.test_context_variations(test)
            if context_results['total'] > 0:
                print(f"   Context tests: {context_results['passed']}/{context_results['total']}")
            
            note = test.get('note', '')
            if note:
                print(f"   Note: {note}")
            
            details.append({
                'input': input_text,
                'passed': basic_pass,
                'context_results': context_results
            })
        
        total = passed + failed
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"\n{'-'*70}")
        print(f"Category Result: {passed}/{total} passed ({percentage:.1f}%)")
        
        return {
            'name': category_name,
            'passed': passed,
            'failed': failed,
            'total': total,
            'percentage': percentage,
            'details': details
        }
    
    def run_all_tests(self):
        """Run all test categories"""
        print("\n" + "="*70)
        print("ADVANCED JAPANESE KANJI TEST SUITE")
        print("="*70)
        print()
        print("🎯 Testing: Context-aware suggestions and learning behavior")
        print("📊 Test File: test-data/test-kanji-v2-cases.json")
        print("="*70)
        
        data = self.load_tests()
        test_categories = data.get('test_categories', [])
        
        all_results = []
        total_passed = 0
        total_failed = 0
        
        for category in test_categories:
            result = self.run_category_tests(category)
            all_results.append(result)
            total_passed += result['passed']
            total_failed += result['failed']
        
        # Summary
        total_tests = total_passed + total_failed
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"\nOverall: {total_passed}/{total_tests} passed ({success_rate:.1f}%)")
        print()
        
        print("Category Breakdown:")
        for result in all_results:
            status = "✅" if result['percentage'] >= 80 else "⚠️" if result['percentage'] >= 60 else "❌"
            print(f"  {status} {result['name']}: {result['passed']}/{result['total']} ({result['percentage']:.1f}%)")
        
        # Analysis
        print(f"\n{'='*70}")
        print("ANALYSIS")
        print(f"{'='*70}")
        
        if success_rate >= 80:
            print("✅ GOOD: Basic homonym suggestions working well")
            print("   - Dictionary covers most common kanji variations")
            print("   - Suggestions include expected alternatives")
        elif success_rate >= 60:
            print("⚠️  ACCEPTABLE: Core functionality present")
            print("   - Basic suggestions working")
            print("   - Context-aware features need enhancement")
        else:
            print("❌ NEEDS IMPROVEMENT: Expand dictionary coverage")
            print("   - Add more kanji variations")
            print("   - Improve homonym handling")
        
        print()
        print("📝 Notes:")
        print("   - This test suite includes advanced features:")
        print("     • Context-aware suggestions")
        print("     • User learning behavior")
        print("     • Compound word prediction")
        print("   - Full implementation requires:")
        print("     • Context analysis engine")
        print("     • User preference tracking")
        print("     • Frequency-based reordering")
        print()
        
        print(f"{'='*70}")
        print("RECOMMENDATION")
        print(f"{'='*70}")
        
        if success_rate >= 70:
            print("✅ Current dictionary provides good baseline coverage")
            print("   Next steps:")
            print("   1. Implement context-aware reordering in Swift")
            print("   2. Add user learning with frequency tracking")
            print("   3. Enhance with compound word prediction")
        else:
            print("⚠️  Expand dictionary before advanced features")
            print("   Priority:")
            print("   1. Add missing homonym variations")
            print("   2. Increase kanji coverage")
            print("   3. Then implement context awareness")
        
        print(f"{'='*70}")
        
        # Save results
        results_file = Path('test-data/advanced-kanji-test-results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_tests': total_tests,
                'passed': total_passed,
                'failed': total_failed,
                'success_rate': success_rate,
                'categories': all_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Results saved to: {results_file}")
        print("="*70)
        
        return success_rate >= 60  # 60% threshold for advanced tests


def main():
    tester = AdvancedKanjiTester()
    success = tester.run_all_tests()
    
    import sys
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
