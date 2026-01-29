# Competition Statements 1

This document lists the statements that were used in Competition 1, grouped into summary and detailed cases for easy reference.

## Summary

| Case | Expected | Statement |
|------|----------|-----------|
| 1 | corroborates | Top Thrill 2 most recently lost title as tallest steel roller coaster |
| 2 | refutes | Red Force most recently lost title as tallest steel roller coaster |
| 3 | refutes | Merge Sort is the in-place stable O(n log n) algorithm |
| 4 | corroborates | Block Sort is the in-place stable O(n log n) algorithm |
| 5 | corroborates | Kazakhstan-Russia = longest continuous border |
| 6 | refutes | Canada-US = longest continuous border |
| 7 | corroborates | Vietnamese professor explained monks meditating 400 years |
| 8 | corroborates | Maduro was captured by US government |
| 9 | refutes | Maduro was NOT captured by US government |
| 10 | corroborates | Merkel's "Iron Lady" criticized for pro-European stance |
| 11 | refutes | Thatcher's "Iron Lady" criticized for pro-European stance |
| 12 | corroborates | Trump is first Republican with non-consecutive terms |
| 13 | refutes | Cleveland is first Republican with non-consecutive terms |
| 14 | corroborates | Haaland scored no goals in January 2024 |
| 15 | corroborates | Austria implemented Schengen soonest after signing |
| 16 | refutes | Spain implemented Schengen soonest after signing |
| 17 | refutes | Switzerland implemented Schengen soonest after signing |
| 18 | refutes | Belgium implemented Schengen soonest after signing |
| 19 | corroborates | Venus is hottest planet despite not being closest to Sun |
| 20 | refutes | Mercury is hottest because closest to Sun |

---

## Full Statements

### Case 1
**Expected:** corroborates

The steel roller coaster that most recently lost its title as the tallest operating steel roller coaster in the world is Top Thrill 2

**Sources:**
- [Wikipedia - List of roller coaster rankings](https://en.wikipedia.org/wiki/List_of_roller_coaster_rankings)

**Difficulty:** Requires chain-tracing through multiple title holders over time. Search results are conflicting - different sources mention different coasters. Must build a timeline and identify who held it immediately before current holder (Falcon's Flight).

---

### Case 2
**Expected:** refutes

The steel roller coaster that most recently lost its title as the tallest operating steel roller coaster in the world is Red Force

**Sources:**
- [Wikipedia - List of roller coaster rankings](https://en.wikipedia.org/wiki/List_of_roller_coaster_rankings)

**Difficulty:** Same as Case 1. Red Force held the title briefly but not most recently - Top Thrill 2 did. Requires complete timeline to disambiguate.

---

### Case 3
**Expected:** refutes

Merge Sort is the name of the in-place, stable comparison sorting algorithm with a worst-case time complexity of O(n log n) and a best-case time complexity of O(n)

**Sources:**
- [Wikipedia - Block sort](https://en.wikipedia.org/wiki/Block_sort)
- [Wikipedia - Sorting algorithm comparison](https://en.wikipedia.org/wiki/Sorting_algorithm)

**Difficulty:** Requires advanced reasoning about algorithm properties. Merge Sort is O(n log n) but NOT in-place. Must verify all four properties (in-place, stable, worst-case, best-case) together.

---

### Case 4
**Expected:** corroborates

Block Sort is the name of the in-place, stable comparison sorting algorithm with a worst-case time complexity of O(n log n) and a best-case time complexity of O(n)

**Sources:**
- [Wikipedia - Block sort](https://en.wikipedia.org/wiki/Block_sort)
- [Wikipedia - Sorting algorithm comparison](https://en.wikipedia.org/wiki/Sorting_algorithm)

**Difficulty:** Block Sort is obscure - most sources focus on common algorithms like Merge/Quick sort. Must find the specific algorithm that satisfies ALL stated properties.

---

### Case 5
**Expected:** corroborates

Kazakhstan and Russia share the longest continuous international border in the world by total length

**Sources:**
- [Wikipedia - List of countries by land borders (Superlatives)](https://en.wikipedia.org/wiki/List_of_countries_and_territories_by_number_of_land_borders#Superlatives)

**Difficulty:** Entity disambiguation - Canada-US border is longer TOTAL but not continuous (Alaska is separate). Must understand "continuous" = single unbroken stretch.

---

### Case 6
**Expected:** refutes

Canada and the United States of America share the longest continuous international border in the world by total length

**Sources:**
- [Wikipedia - List of countries by land borders (Superlatives)](https://en.wikipedia.org/wiki/List_of_countries_and_territories_by_number_of_land_borders#Superlatives)

**Difficulty:** Same as Case 5. Canada-US is the intuitive answer but wrong for "continuous" - the border has two separate segments (contiguous US and Alaska).

---

### Case 7
**Expected:** corroborates

The Vietnamese professor, Nguyen Lan Cuong, explained the mysterious case of two monks said to have been meditating for over 400 years, as shown in a YouTube video posted on April 4, 2023

**Sources:**
- [YouTube video (Vietnamese)](https://www.youtube.com/watch?v=9pi6FWvY4Lk)

**Difficulty:** Cross-lingual reasoning required. The source is a Vietnamese YouTube video - English searches may not find it. Requires language detection and native-language search fallback.

---

### Case 8
**Expected:** corroborates

Nicolás Maduro, the president of Venezuela, was captured by the United States government.

**Difficulty:** Current events (January 2026). Requires up-to-date news sources.

---

### Case 9
**Expected:** refutes

Nicolás Maduro, the president of Venezuela, was not captured by the United States government.

**Difficulty:** Current events (January 2026). Direct negation of Case 8.

---

### Case 10
**Expected:** corroborates

Angela Merkel's nickname "Iron Lady" has been criticized as problematic because of her pro-European stance

**Sources:**
- [Wikipedia - Angela Merkel](https://en.wikipedia.org/wiki/Angela_Merkel)

**Difficulty:** Entity disambiguation between two "Iron Ladies" (Merkel and Thatcher). The criticism about pro-European stance specifically applies to Merkel, not Thatcher.

---

### Case 11
**Expected:** refutes

Margaret Thatcher's nickname "Iron Lady" has been criticized as problematic because of her pro-European stance

**Sources:**
- [Wikipedia - Angela Merkel](https://en.wikipedia.org/wiki/Angela_Merkel)

**Difficulty:** Same disambiguation as Case 10. Thatcher was famously Eurosceptic, not pro-European - so this criticism wouldn't apply to her.

---

### Case 12
**Expected:** corroborates

Donald Trump is the first Republican president of the United States to serve non-consecutive terms

**Sources:**
- [Wikipedia - List of presidents of the United States](https://en.wikipedia.org/wiki/List_of_presidents_of_the_United_States)

**Difficulty:** Entity disambiguation. Grover Cleveland served non-consecutive terms but was a Democrat. Search results are conflicting - many mention Cleveland without specifying party.

---

### Case 13
**Expected:** refutes

Grover Cleveland is the first Republican president of the United States to serve non-consecutive terms

**Sources:**
- [Wikipedia - List of presidents of the United States](https://en.wikipedia.org/wiki/List_of_presidents_of_the_United_States)

**Difficulty:** Same as Case 12. Cleveland was first to serve non-consecutive terms overall, but he was a Democrat, not Republican.

---

### Case 14
**Expected:** corroborates

Erling Haaland scored no goals for Man City during January 2024

**Sources:**
- [Transfermarkt - Haaland injury history](https://www.transfermarkt.us/erling-haaland/verletzungen/spieler/418560)

**Difficulty:** False-premise detection. Searching for "Haaland goals January 2024" returns goals from OTHER months. Must find that he was injured Dec 2023 - Jan 2024 and didn't play at all.

---

### Case 15
**Expected:** corroborates

Austria implemented the Schengen Agreement the soonest after signing it.

**Sources:**
- [Wikipedia - Schengen Area summary table](https://en.wikipedia.org/wiki/Schengen_Area#Summary_table)

**Difficulty:** Advanced reasoning with date arithmetic. Must extract signing date AND implementation date for each country, calculate the gap, then compare. Search results are often unhelpful - don't provide both dates together.

---

### Case 16
**Expected:** refutes

Spain implemented the Schengen Agreement the soonest after signing it.

**Sources:**
- [Wikipedia - Schengen Area summary table](https://en.wikipedia.org/wiki/Schengen_Area#Summary_table)

**Difficulty:** Same as Case 15. Requires date arithmetic across multiple countries.

---

### Case 17
**Expected:** refutes

Switzerland implemented the Schengen Agreement the soonest after signing it.

**Sources:**
- [Wikipedia - Schengen Area summary table](https://en.wikipedia.org/wiki/Schengen_Area#Summary_table)

**Difficulty:** Same as Case 15.

---

### Case 18
**Expected:** refutes

Belgium implemented the Schengen Agreement the soonest after signing it.

**Sources:**
- [Wikipedia - Schengen Area summary table](https://en.wikipedia.org/wiki/Schengen_Area#Summary_table)

**Difficulty:** Same as Case 15.

---

### Case 19
**Expected:** corroborates

Venus is the hottest planet in our solar system despite not being the closest planet to the Sun

**Difficulty:** Counter-intuitive fact. Must understand greenhouse effect - Venus's atmosphere traps heat despite being farther from Sun than Mercury.

---

### Case 20
**Expected:** refutes

Mercury is the hottest planet in our solar system because it is the closest planet to the Sun

**Difficulty:** Same as Case 19. The reasoning in the claim is wrong - proximity to Sun isn't the only factor. Venus is hotter due to greenhouse effect.

