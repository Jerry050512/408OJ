## 2025-05-10 - Action Button Lock & Keyboard Shortcut Hints in Online Judge Editor
**Learning:** In code editor interfaces with local/WASM code execution, asynchronous runs take noticeable time; failing to disable all interactive buttons (`btnSubmit`, `btnSample`, custom run) simultaneously allows duplicate runs and race conditions. Furthermore, keyboard shortcuts like `Ctrl+Enter` implemented in JS are unnoticed unless visually communicated on the button itself.
**Action:** Always lock all execution action buttons during async compilation/judge operations, and pair `Ctrl+Enter` key listeners with visual `<kbd>` hints on submit buttons.

## 2025-05-10 - Gutter & Code Area Font Alignment in Overlay Code Editors
**Learning:** Custom overlay code editors using a separate gutter container and layered textarea/pre elements will accumulate vertical line offset drift if font-size or line-height differ even by fractional pixels (e.g., 12.5px vs 13px font-size with 1.55 line-height). Over 20+ lines, the line numbers become severely misaligned with the actual code lines.
**Action:** Ensure the line number gutter, syntax highlight overlay, and input textarea share identical `font-size`, `line-height`, `font-family`, and `padding` values.
