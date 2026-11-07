# Architecture

The library follows a linear pipeline: `load_answers` -> `assess` -> `render`.

1. `Answers` (data class): Represents the validated configuration of the system.
2. `Assessment` (data class): The output structure containing category, list of `Obligation` objects, and notes.
3. `DEFAULT_TABLE`: A `Mapping` of `ObligationRow` entries containing articles, titles, and application dates derived from EU 2024/1689 and 2026/1744.