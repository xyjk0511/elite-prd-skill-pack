# PRD Pipeline Gates

Use these gates to decide whether to continue, stop, or return to an earlier stage.

## Stage Gates

| Stage | Continue When | Stop / Return When |
|---|---|---|
| Product discussion | User selected and discussed at least one gray area, or explicitly chose auto/direct mode | User has not discussed any gray area and did not authorize auto mode |
| Requirements clarity | Clarity score >= 85, or 70-84 with explicit assumptions | Score < 50, or core target user/problem/scope missing |
| PRD writing | Scope, P0 requirements, state, permission, fields, analytics, and acceptance criteria are present | Missing P0 acceptance criteria, scope boundary, state machine, or permissions |
| PRD audit | Audit says “可以开工” or “补充后开工” without P0 blockers | Audit says “暂不建议开工” or has P0 blockers |
| Handoff | PRD and audit packets are available, implementation blockers are explicit | Handoff exposes missing product decisions |
| QA generation | PRD has testable acceptance criteria and enough state/permission/field rules | QA cannot cover P0 paths due to missing PRD details |

## Required Packets

```text
PRD Discussion Context -> Requirements Packet -> PRD Packet -> Audit Packet -> Handoff Packet -> QA Packet
```

Each packet should preserve paths, scope, blockers, and next-step status.
