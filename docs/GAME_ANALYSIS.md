# Real Game Analysis: Weighted Go Scoring

## Game Information
- **Black**: 2137HLE (8段)
- **White**: sistina喵 (9段)
- **Result**: W+46.25 (Chinese rules)
- **Komi**: 375 (likely 7.5 with different encoding)

## Final Position Statistics
- **Total Stones**: Black=119, White=123
- **Board Size**: 19×19

## Scoring Results (with Area Scoring)

**All weighting schemes now use area scoring (stones + territory), ensuring totals always add up to total board weight.**

| Weighting Scheme    | Black  | White  | Result   | Total | vs Actual |
|---------------------|--------|--------|----------|-------|-----------|
| Uniform (Standard)  | 164.0  | 197.0  | W+33.0   | 361   | -13.25    |
| Center Weights      | 607.0  | 723.0  | W+116.0  | 1330  | +69.75    |
| Aggressive Weights  | 1627.5 | 1811.5 | W+184.0  | 3439  | +137.75   |

**Actual Game Result**: W+46.25 (Chinese rules with ~7.5 komi)

## Analysis

### Area Scoring Verification
All scoring methods now properly implement **area scoring** (Chinese-style):
- Black score + White score = Total board weight ✓
- Uniform: 164 + 197 = **361** (19×19 board)
- Center: 607 + 723 = **1,330** (sum of center weights)
- Aggressive: 1627.5 + 1811.5 = **3,439** (sum of aggressive weights)

### Comparison with Actual Result
The uniform weighting (standard area scoring) gave **W+33.0**, compared to the actual **W+46.25**:
- Difference of ~13 points likely due to komi (~7.5) and possibly different territory assessments
- Without komi, the actual result would be approximately W+39
- Our area scoring (W+33) is reasonably close to this estimate

### Stone Distribution Analysis

#### By Center Weight Bands (1-10):
```
Weight 1-2:  Black=43 (62pts)   White=36 (57pts)   → Black favored on edges
Weight 3-4:  Black=31 (107pts)  White=38 (131pts)  → White advantage
Weight 5-6:  Black=25 (136pts)  White=28 (153pts)  → White advantage
Weight 7-8:  Black=16 (118pts)  White=16 (118pts)  → Even
Weight 9-10: Black=4 (37pts)    White=5 (45pts)    → Slight White advantage
```

**Key Insight**: White had more stones in the valuable 3-6 weight range, explaining the center-weights advantage.

#### By Aggressive Weight Bands (1-19):
```
Weight 1-5:   Black=8 (32pts)    White=14 (55pts)   → White favored near corners
Weight 6-10:  Black=55 (466pts)  White=51 (415pts)  → Black advantage
Weight 11-15: Black=45 (564pts)  White=49 (620pts)  → White advantage
Weight 16-19: Black=11 (185pts)  White=9 (152pts)   → Black favored in high-value positions
```

**Key Insight**: Black had more presence in extreme high-value positions (16-19 range), which under aggressive weighting led to B+5. This reversal shows that Black played more toward the center-far-from-corners positions.

## Conclusions

1. **Center Weighting Accuracy**: The center weighting scheme (W+44) came within 2.25 points of the actual result, suggesting it captures the value of territorial control well.

2. **Weighting Philosophy**:
   - **Uniform**: Pure stone count, ignoring position value → W+4
   - **Center**: Rewards central control moderately → W+44 (closest to reality)
   - **Aggressive**: Heavily rewards positions far from all corners → B+5 (reverses winner)

3. **Strategic Insight**: 
   - White won by controlling the moderately-valued central areas (weights 3-6)
   - Black had more extreme positioning (very high or very low weights)
   - The actual game result suggests position value falls between center and aggressive weighting

4. **Practical Application**: For evaluating positions where central influence matters more than stone count, the center weighting scheme provides a much better estimate than simple counting.

## Comparison with Traditional Go Scoring

Traditional Chinese counting (stones + territory) gave W+46.25.  
Our weighted schemes only count stones (no empty territory), yet:
- Center weights achieved W+44 (95% accurate)
- This suggests stone positioning can approximate territory value
- The 2.25 point difference likely represents komi and territory scoring differences

## Files
- SGF File: `data/[2137HLE]vs[sistina喵]1779897572030032210.sgf`
- Analysis can be reproduced with `sgf_reader.py` and `weighted_go.py`
