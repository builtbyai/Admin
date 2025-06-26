# Readability Calculation Formulas

## Flesch Reading Ease
**Formula**: 206.835 - 1.015(total words/total sentences) - 84.6(total syllables/total words)

**Score Interpretation**:
- 90-100: Very Easy (5th grade)
- 80-89: Easy (6th grade)
- 70-79: Fairly Easy (7th grade)
- 60-69: Standard (8th-9th grade)
- 50-59: Fairly Difficult (10th-12th grade)
- 30-49: Difficult (college level)
- 0-29: Very Difficult (graduate level)

## Flesch-Kincaid Grade Level
**Formula**: 0.39(total words/total sentences) + 11.8(total syllables/total words) - 15.59

**Output**: Direct grade level (e.g., 8.5 = 8th-9th grade reading level)

## Automated Readability Index (ARI)
**Formula**: 4.71(characters/words) + 0.5(words/sentences) - 21.43

**Advantages**: Uses character count instead of syllables for more consistent results

## Syllable Counting Rules

### Basic Rules
1. Count vowel groups (a, e, i, o, u, y) as one syllable
2. Silent 'e' at end doesn't count (except when it's the only vowel)
3. Consecutive vowels usually count as one syllable
4. 'y' counts as vowel when it sounds like a vowel

### Special Cases
- Words ending in 'le' preceded by consonant: add 1 syllable
- Compound words: count syllables in each part
- Minimum 1 syllable per word

### Implementation Example
```python
def count_syllables(word):
    word = word.lower()
    vowels = 'aeiouy'
    syllable_count = 0
    previous_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel
    
    # Handle silent 'e'
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1
    
    return max(1, syllable_count)
```

## Reading Time Calculation
- **Average reading speed**: 200-250 words per minute
- **Formula**: (word_count / 225) * 60 = seconds
- **Adjust for complexity**: Add 10-20% for technical content
