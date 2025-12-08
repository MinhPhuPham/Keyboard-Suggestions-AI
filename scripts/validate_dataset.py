"""
Dataset statistics and validation
"""

import json
from pathlib import Path
from collections import Counter
from typing import Dict, List


def analyze_dataset(file_path: Path, language: str = 'en') -> Dict:
    """Analyze training dataset statistics"""
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    if not lines:
        print(f"Warning: No data in {file_path}")
        return {}
    
    # Basic stats
    total_sentences = len(lines)
    total_words = sum(len(line.split()) for line in lines)
    total_chars = sum(len(line) for line in lines)
    
    # Word length distribution
    word_lengths = [len(line.split()) for line in lines]
    
    # Character frequency
    all_text = ''.join(lines)
    char_freq = Counter(all_text)
    
    # Emoji count (Unicode > 0x1F300)
    emoji_count = sum(1 for c in all_text if ord(c) > 0x1F300)
    
    # Unique words
    all_words = ' '.join(lines).split()
    unique_words = len(set(all_words))
    
    stats = {
        'file': str(file_path),
        'language': language,
        'total_sentences': total_sentences,
        'total_words': total_words,
        'total_characters': total_chars,
        'unique_words': unique_words,
        'avg_words_per_sentence': total_words / total_sentences,
        'avg_chars_per_sentence': total_chars / total_sentences,
        'min_words': min(word_lengths),
        'max_words': max(word_lengths),
        'emoji_count': emoji_count,
        'unique_characters': len(char_freq),
        'vocabulary_richness': unique_words / total_words if total_words > 0 else 0
    }
    
    return stats


def print_stats(stats: Dict):
    """Print formatted statistics"""
    if not stats:
        return
    
    print(f"\n{'='*70}")
    print(f"Dataset Analysis: {Path(stats['file']).name}")
    print(f"{'='*70}")
    print(f"Language:              {stats['language']}")
    print(f"Total sentences:       {stats['total_sentences']:,}")
    print(f"Total words:           {stats['total_words']:,}")
    print(f"Unique words:          {stats['unique_words']:,}")
    print(f"Avg words/sentence:    {stats['avg_words_per_sentence']:.1f}")
    print(f"Avg chars/sentence:    {stats['avg_chars_per_sentence']:.1f}")
    print(f"Word range:            {stats['min_words']}-{stats['max_words']}")
    print(f"Emoji count:           {stats['emoji_count']}")
    print(f"Unique characters:     {stats['unique_characters']}")
    print(f"Vocabulary richness:   {stats['vocabulary_richness']:.3f}")
    
    # Quality assessment
    print(f"\n{'Quality Assessment':^70}")
    print(f"{'-'*70}")
    
    # Check if dataset is large enough
    if stats['total_sentences'] < 1000:
        print("⚠️  Dataset is small (<1,000 sentences)")
        print("   Recommendation: Collect more data for better model quality")
    elif stats['total_sentences'] < 10000:
        print("⚠️  Dataset is moderate (1K-10K sentences)")
        print("   Recommendation: Aim for 10,000+ sentences for production")
    else:
        print("✅ Dataset size is good (10,000+ sentences)")
    
    # Check vocabulary richness
    if stats['vocabulary_richness'] < 0.1:
        print("⚠️  Low vocabulary diversity")
        print("   Recommendation: Add more varied text sources")
    else:
        print("✅ Good vocabulary diversity")
    
    # Check average sentence length
    if stats['avg_words_per_sentence'] < 5:
        print("⚠️  Sentences are very short")
    elif stats['avg_words_per_sentence'] > 30:
        print("⚠️  Sentences are very long")
    else:
        print("✅ Sentence length is appropriate")


def validate_dataset_quality(file_path: Path, min_sentences: int = 1000) -> bool:
    """
    Validate if dataset meets minimum quality requirements.
    
    Returns:
        True if dataset is valid, False otherwise
    """
    stats = analyze_dataset(file_path)
    
    if not stats:
        return False
    
    # Check minimum size
    if stats['total_sentences'] < min_sentences:
        print(f"❌ Dataset too small: {stats['total_sentences']} < {min_sentences}")
        return False
    
    # Check vocabulary richness
    if stats['vocabulary_richness'] < 0.05:
        print(f"❌ Vocabulary too limited: {stats['vocabulary_richness']:.3f}")
        return False
    
    # Check average sentence length
    if stats['avg_words_per_sentence'] < 3:
        print(f"❌ Sentences too short: {stats['avg_words_per_sentence']:.1f}")
        return False
    
    print(f"✅ Dataset quality check passed")
    return True


if __name__ == "__main__":
    print("="*70)
    print("Dataset Statistics & Validation")
    print("="*70)
    
    # Analyze all datasets
    datasets = [
        ('data/processed/english_clean.txt', 'en'),
        ('data/processed/japanese_clean.txt', 'ja'),
        ('data/processed/combined_train.txt', 'multilingual'),
    ]
    
    all_stats = []
    
    for file_path, lang in datasets:
        path = Path(file_path)
        if path.exists():
            stats = analyze_dataset(path, lang)
            if stats:
                print_stats(stats)
                all_stats.append(stats)
        else:
            print(f"\nSkipped: {file_path} (not found)")
    
    # Save stats to JSON
    if all_stats:
        output_file = 'data/dataset_stats.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_stats, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*70}")
        print(f"Statistics saved to: {output_file}")
        print(f"{'='*70}")
        
        # Overall summary
        total_sentences = sum(s['total_sentences'] for s in all_stats)
        total_words = sum(s['total_words'] for s in all_stats)
        
        print(f"\nOverall Summary:")
        print(f"  Total datasets: {len(all_stats)}")
        print(f"  Total sentences: {total_sentences:,}")
        print(f"  Total words: {total_words:,}")
        
        # Recommendations
        print(f"\n{'Recommendations':^70}")
        print(f"{'-'*70}")
        
        if total_sentences < 10000:
            print("📊 Current dataset: Demo/Testing quality")
            print("🎯 Target for production: 20,000+ sentences")
            print("📈 Recommended next steps:")
            print("   1. Collect more English casual text (target: 10,000+)")
            print("   2. Collect more Japanese polite text (target: 10,000+)")
            print("   3. Add emoji-rich examples (target: 500+)")
            print("   4. Add mixed language examples (target: 200+)")
        else:
            print("✅ Dataset is ready for production training!")
            print("💡 Optional improvements:")
            print("   - Add more diverse sources")
            print("   - Balance language distribution")
            print("   - Include domain-specific vocabulary")
