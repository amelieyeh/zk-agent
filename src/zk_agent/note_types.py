"""
Shared Zettelkasten note type definitions.

Single source of truth for classifier and detector prompts.
"""

DEFINITIONS = """\
- **fleeting**: A raw thought, quick observation, or unprocessed idea. Not yet \
developed. Often contains "maybe", "what if", questions, or todos.
- **literature**: An insight derived from an external source (article, talk, \
book, product, documentation, someone else's idea). The key test: could you \
cite where this came from? If yes, it's literature.
- **permanent**: Your own synthesized conclusion that connects multiple ideas \
or domains. This is an original thought that stands on its own — it draws \
parallels, makes analogies, proposes frameworks, or reveals a pattern."""

BOUNDARY_RULES = """\
- References an external source AND adds original synthesis → **permanent** \
(the synthesis is the value, not the reference)
- States facts from a source without adding interpretation → **literature**
- A question that embeds a hypothesis ("maybe X works because Y") → **fleeting**
- An observation that could become a framework but isn't developed → **fleeting**
- When genuinely ambiguous, prefer **fleeting** (lower commitment, can be promoted later)"""
