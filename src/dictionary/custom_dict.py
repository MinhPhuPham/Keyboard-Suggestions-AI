"""
Custom Dictionary System
Fast prefix-based lookup for user-defined mappings
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import bisect


class PrefixTrie:
    """
    Trie data structure for fast prefix search.
    Optimized for custom dictionary lookups.
    """
    
    class TrieNode:
        def __init__(self):
            self.children = {}
            self.is_end = False
            self.value = None
    
    def __init__(self):
        self.root = self.TrieNode()
    
    def insert(self, key: str, value: str):
        """Insert key-value pair into trie"""
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = self.TrieNode()
            node = node.children[char]
        node.is_end = True
        node.value = value
    
    def search(self, key: str) -> Optional[str]:
        """Search for exact key match"""
        node = self.root
        for char in key:
            if char not in node.children:
                return None
            node = node.children[char]
        return node.value if node.is_end else None
    
    def prefix_search(self, prefix: str) -> List[Tuple[str, str]]:
        """
        Find all key-value pairs with given prefix.
        
        Args:
            prefix: Prefix to search for
        
        Returns:
            List of (key, value) tuples
        """
        results = []
        
        # Navigate to prefix node
        node = self.root
        for char in prefix:
            if char not in node.children:
                return results
            node = node.children[char]
        
        # DFS to find all completions
        self._dfs_collect(node, prefix, results)
        
        return results
    
    def _dfs_collect(self, node: TrieNode, current_key: str, results: List[Tuple[str, str]]):
        """DFS helper to collect all values under a node"""
        if node.is_end:
            results.append((current_key, node.value))
        
        for char, child in node.children.items():
            self._dfs_collect(child, current_key + char, results)


class CustomDictionary:
    """
    Custom dictionary for user-defined text expansions.
    Supports fast prefix lookup and hot-reload.
    """
    
    def __init__(self, dict_file: Optional[str] = None):
        self.trie = PrefixTrie()
        self.entries = {}  # key -> value mapping
        self.dict_file = dict_file
        
        if dict_file and Path(dict_file).exists():
            self.load(dict_file)
    
    def add(self, key: str, value: str, priority: int = 1):
        """
        Add custom dictionary entry.
        
        Args:
            key: Trigger key (e.g., "ty")
            value: Expansion value (e.g., "thank you")
            priority: Priority for ranking (higher = more important)
        """
        key = key.lower().strip()
        value = value.strip()
        
        self.entries[key] = {
            'value': value,
            'priority': priority
        }
        
        self.trie.insert(key, value)
    
    def remove(self, key: str):
        """Remove dictionary entry"""
        key = key.lower().strip()
        if key in self.entries:
            del self.entries[key]
            # Rebuild trie
            self._rebuild_trie()
    
    def get(self, key: str) -> Optional[str]:
        """Get exact match for key"""
        key = key.lower().strip()
        entry = self.entries.get(key)
        return entry['value'] if entry else None
    
    def prefix_search(self, prefix: str, max_results: int = 5) -> List[str]:
        """
        Search for entries matching prefix.
        
        Args:
            prefix: Prefix to search for
            max_results: Maximum number of results
        
        Returns:
            List of expansion values
        """
        prefix = prefix.lower().strip()
        
        # Get all matches from trie
        matches = self.trie.prefix_search(prefix)
        
        # Sort by priority (if available) and key length
        sorted_matches = sorted(
            matches,
            key=lambda x: (
                -self.entries.get(x[0], {}).get('priority', 0),
                len(x[0])
            )
        )
        
        # Return values only
        results = [value for key, value in sorted_matches[:max_results]]
        
        return results
    
    def _rebuild_trie(self):
        """Rebuild trie from entries"""
        self.trie = PrefixTrie()
        for key, entry in self.entries.items():
            self.trie.insert(key, entry['value'])
    
    def save(self, file_path: str):
        """Save dictionary to JSON file"""
        data = {
            'version': '1.0',
            'entries': self.entries
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, file_path: str):
        """Load dictionary from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.entries = data.get('entries', {})
        self._rebuild_trie()
    
    def reload(self):
        """Hot-reload dictionary from file"""
        if self.dict_file and Path(self.dict_file).exists():
            self.load(self.dict_file)
    
    def get_stats(self) -> Dict:
        """Get dictionary statistics"""
        return {
            'total_entries': len(self.entries),
            'avg_key_length': sum(len(k) for k in self.entries) / max(len(self.entries), 1),
            'avg_value_length': sum(len(e['value']) for e in self.entries.values()) / max(len(self.entries), 1)
        }


def create_default_dictionary(output_file: str = "config/custom_dictionary.json"):
    """
    Create default custom dictionary with common abbreviations.
    
    Args:
        output_file: Path to save dictionary
    """
    dictionary = CustomDictionary()
    
    # Common abbreviations
    common_entries = [
        ("ty", "thank you", 1),
        ("brb", "be right back", 1),
        ("omw", "on my way", 1),
        ("idk", "I don't know", 1),
        ("tbh", "to be honest", 1),
        ("imo", "in my opinion", 1),
        ("btw", "by the way", 1),
        ("fyi", "for your information", 1),
        ("asap", "as soon as possible", 1),
        ("lmk", "let me know", 1),
        ("nvm", "never mind", 1),
        ("gtg", "got to go", 1),
        ("ttyl", "talk to you later", 1),
        ("np", "no problem", 1),
        ("yw", "you're welcome", 1),
        ("gg", "good game", 1),
        ("afk", "away from keyboard", 1),
        ("dm", "direct message", 1),
        ("irl", "in real life", 1),
        # Custom example from spec
        ("ac", "scackscac", 2),  # Higher priority
    ]
    
    for key, value, priority in common_entries:
        dictionary.add(key, value, priority)
    
    # Save to file
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    dictionary.save(output_file)
    
    print(f"Created default dictionary: {output_file}")
    print(f"Total entries: {len(common_entries)}")
    
    return dictionary


if __name__ == "__main__":
    # Create default dictionary
    dictionary = create_default_dictionary()
    
    # Test prefix search
    print("\nTesting prefix search:")
    print("-" * 50)
    
    test_prefixes = ["t", "ty", "b", "i", "ac"]
    
    for prefix in test_prefixes:
        results = dictionary.prefix_search(prefix)
        print(f"\nPrefix: '{prefix}'")
        print(f"Results: {results}")
    
    # Test exact match
    print("\n\nTesting exact match:")
    print("-" * 50)
    
    test_keys = ["ty", "brb", "ac", "xyz"]
    
    for key in test_keys:
        value = dictionary.get(key)
        print(f"Key: '{key}' -> Value: '{value}'")
    
    # Show stats
    print("\n\nDictionary stats:")
    print("-" * 50)
    stats = dictionary.get_stats()
    for key, value in stats.items():
        print(f"{key}: {value:.2f}" if isinstance(value, float) else f"{key}: {value}")
