  1. How the Matching Works
  The matching uses a "Normalization-First" exact merge strategy:
   * Normalization: Both PyPI distribution names and GitHub detected import
     names are converted to a canonical form: lowercase, hyphens instead of
     underscores (e.g., PyYAML or pyyaml_lib → pyyaml), and whitespace trimmed.
   * Merge Logic:
       1. We take the GitHub library-week panel and merge it with the PyPI
          release table. This filters GitHub data to only include libraries with
          a verifiable PyPI release date.
       2. We then do a left join from the PyPI "universe" to this GitHub
          aggregate. This allows us to track libraries that exist on PyPI but
          have zero recorded imports on GitHub.

  2. What Exactly is Being Matched
   * PyPI Distribution Name: The name used in pip install package_name.
   * GitHub Import Name: The name used in import library_name within Python
     scripts.
     
✦ The mystery is solved! The difference is entirely in the perspective (the
  denominator).

  1. The GitHub Perspective (The 33.1% result)
  When you ask, "What percentage of libraries mentioned on GitHub are on PyPI?",
  you get 33.1%.
   * Total unique GitHub library names: 163,083
   * Unique matches to PyPI: 53,972
   * Conclusion: GitHub is full of "noise" like standard library modules,
     internal project imports, and non-PyPI dependencies. Only about 1 in 3
     unique library names found in GitHub code actually comes from a PyPI
     package.

  2. The PyPI Perspective (The 6.2% result)
  When you ask, "What percentage of PyPI packages ever appear on GitHub?", you
  get 6.2%.
   * Total unique PyPI packages: 871,133
   * Unique matches to GitHub: 53,972
   * Conclusion: Most PyPI packages (93.8%) are "ghost packages"—they are
     released but never gain enough adoption to show up in our GitHub data
     panel.
     
  What this shows is:
   * Our matching logic is actually exactly the same as the other LLM's (we both
     get 53,972 matches).
   * Our current simple normalization (lower case + hyphens) is already very
     effective.
   * The 33% vs. 6% difference is just two different ways of looking at the same
     53,972 matched pairs.