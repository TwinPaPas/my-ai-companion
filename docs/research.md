# Similar projects — checked 2026-11-19 (KST)

These are source-document findings, not installation or performance tests. No source code or assets from these projects are incorporated.

| Project | Evidence | Overlap / distinction |
|---|---|---|
| [my-agent-girlfriend](https://github.com/aldegad/my-agent-girlfriend) | [SKILL source](https://github.com/aldegad/my-agent-girlfriend/blob/main/SKILL.md) explicitly keeps girlfriend mode for the current thread until off; Codex/Claude; names persisted | Very close existing-host mode; fixed anime persona/macOS overlay. In-thread persistence is not proof of global new-thread persistence. |
| [ai-companion-skill](https://github.com/xnydl/ai-companion-skill) | [SKILL source](https://github.com/xnydl/ai-companion-skill/blob/main/SKILL.md): custom names, tastes, relationship, text character cards and memories | Very close text imagination/customization; agent follows instructions to manage files; no tested deterministic care system established here. |
| [girlfriend-agent](https://github.com/Elephenman/girlfriend-agent) | README: personality, episodic memory, relationship growth, CLI/MCP, session hooks | Overlaps growth and persistent character context. Claimed test counts were not independently run. |
| [girlfriend-in-cli](https://github.com/NomaDamas/girlfriend-in-cli) | README: terminal romance, customizable personas, mood, saved/resumed sessions | CLI romance itself is not new. |
| [VAPE](https://github.com/syahiidkamil/vibe-ai-partner-entity) | README: Claude Code/Codex, file-based identity and memory, diary, avatar | Close coding-agent companion with identity persistence. |
| [Sara](https://github.com/farena-ai/sara) | README: companion/coding partner, terminal, MCP, memory and personality | Companion plus real work is already explored. |
| [HerAndHim](https://github.com/ericwang915/HerAndHim) | README: self-hosted boyfriend/girlfriend, memory and `herandhim chat` | Persistent relationship with terminal conversation. |
| [Buddy](https://github.com/fiorastudio/buddy) | README: MCP pet, reactions, XP and SQLite. Memory tool says not robust; dream tool is a placeholder | Care/growth around coding. Do not market roadmap placeholders as implemented facts. |
| [Claude Code Tamagotchi](https://github.com/Ido-Levi/claude-code-tamagotchi) | README: feed/play/pet/clean/sleep commands; hunger, energy, happiness | Direct overlap with CLI care loop; pet-focused, also includes a separate experimental behavior-monitoring feature. |
| [Utsuwa](https://github.com/JuiceBoxxGames/utsuwa) | [Architecture](https://github.com/JuiceBoxxGames/utsuwa/blob/main/src/content/docs/technology/companion-system.md): app-owned relationship/mood state, bounded LLM changes | Strong reference for independent mood, trust, affection and remembered causes; web/desktop presentation. |
| [JunOS](https://github.com/efficiencyx/JunOS) | README: affection/trust/tension respond to interaction, shared activities, anger/refusal | Non-obedient relationship dynamics already exist; game-specific character/web app. |
| [Replika](https://help.replika.com/hc/en-us/articles/115001070951-What-is-Replika) | Official help: friend, romantic partner, mentor, memories and personality | Relationship selection and growing together are established concepts. |

## Conclusion
AI romance, custom characters, CLI companions, care loops, and anger/repair all have precedents. The proposed combination is a product hypothesis, not a novelty claim: a small Korean-first relationship layer for existing AI, with three central relationship modes and observable care/repair across sessions. Whether it is fun or attracts users remains untested.

## Integration references
- [Codex hooks](https://learn.chatgpt.com/docs/hooks): project/user hooks; trust review; SessionStart and UserPromptSubmit additionalContext.
- [Claude Code hooks](https://code.claude.com/docs/en/hooks): lifecycle inputs/outputs and hook configuration.
- Local CLI help was checked during implementation; release verification records exact versions and runtime observations.
