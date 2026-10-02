# Structural language

The numerical labels describe structural relationships, not exact mathematical identities.

Working interpretation:

- first digit: base structural unit
- second digit: approximate proportion of a subsequent leg
  - 1: approximately equal to the base unit
  - 2: approximately double the base unit
- third digit: reaction/evolution information within the structure

Examples such as 0.95, 1.10 or 0.87 may still belong to the "1" family depending on context and tolerance.

The engine must therefore store measured ratios and tolerance decisions rather than comparing floats for equality.

## Important

The exact semantic meaning of every digit and every valid transition still requires labelled visual ground truth.

Where the definition is not yet sufficiently precise, use:

`NEEDS_VISUAL_GROUND_TRUTH`

Do not invent a convenient definition merely to make a detector easier to code.
