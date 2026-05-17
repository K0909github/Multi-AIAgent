# Code Modification Notes

- Parameterize the fusion module and readout head behind config flags.
- Expose ablation toggles so each hypothesis can be tested independently.
- Keep experiment results in machine-readable JSON for later paper drafting.
- Add a small runner script so Copilot can invoke one experiment at a time.
