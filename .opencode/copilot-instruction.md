# Copilot Custom Instructions
Fai sempre riferimento alle convenzioni aziendali e al workflow definiti in:
@AGENTS.md
EOF

cat << 'EOF' > .vscode/settings.json
{
  "gemini.codeAssist.customInstructions": "Segui sempre le convenzioni e i workflow definiti nel file AGENTS.md nella radice del progetto."
}