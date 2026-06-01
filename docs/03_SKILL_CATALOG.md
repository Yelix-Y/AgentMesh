# AgentMesh — Communication Protocol Catalog (ACP)

> In AgentMesh, agents have no "skills" they invoke as tools. Their only capability for coordination is **sending messages**. This catalog defines the Agent Communication Protocol (ACP): the vocabulary of typed messages agents use to collaborate. It is the natural-language equivalent of a skill/tool catalog.

## 1. Message Anatomy

Every interaction is an `ACPMessage`:

```json
{
  "id": "uuid",
  "thread_id": "uuid",
  "sender_id": "alex",
  "recipient_id": "jordan",
  "message_type": "COMPLETION_REPORT",
  "body": "I implemented the OAuth refresh flow. Tokens rotate every 30 min. Watch the clock-skew edge case on token expiry.",
  "metadata": {},
  "created_at": "2026-06-01T09:00:00Z",
  "read": false
}
```

- **`message_type`** declares *intent* (see §2). It is **not** a function signature.
- **`body`** is free-form natural language — the actual content of the communication.
- **`thread_id`** ties related messages into a conversation that any party can replay via `get_thread`.
- **`metadata`** is an optional bag for structured hints (e.g. task id), never a substitute for the natural-language body.

## 2. Message Type Reference

| Type | Typical Sender → Recipient | Purpose | Body should contain |
|---|---|---|---|
| `TASK_HANDOFF` | human→agent, agent→agent | Pass work forward | The goal, relevant context, constraints |
| `CLARIFICATION_REQUEST` | agent→sender | Resolve ambiguity before acting | The specific question and why it matters |
| `STATUS_UPDATE` | agent→peer/human | Signal progress | What's done, what's next, any risk |
| `COMPLETION_REPORT` | agent→next agent | "I'm done" handoff | What was built/found and what to watch out for |
| `REJECTION` | agent→sender | Decline or bounce back | Why, and what would unblock acceptance |
| `ESCALATION` | agent→human | Blocked, needs a human | The blocker and the decision required |
| `REVIEW_REQUEST` | agent→reviewer | Ask for review | What to review and the acceptance bar |
| `REVIEW_DECISION` | reviewer→agent | Approve or request changes | The verdict and concrete, actionable feedback |
| `HUMAN_INTERVENTION` | human→agent | Operator-injected guidance | Any instruction from the operator |

## 3. Canonical Conversations

### 3.1 Standard delivery thread

```text
human  --TASK_HANDOFF-->        Alex      "Build an OAuth refresh token flow."
Alex   --COMPLETION_REPORT-->   Jordan    "Done. Here's the design and the risky edge cases."
Jordan --COMPLETION_REPORT-->   Morgan    "Tested. Found a clock-skew bug on expiry."
Morgan --REVIEW_DECISION-->     Alex      "Changes requested: handle clock skew, then re-submit."
```

### 3.2 Blocked / ambiguous

```text
Alex   --CLARIFICATION_REQUEST--> human   "Should refresh tokens be single-use or reusable?"
human  --HUMAN_INTERVENTION-->    Alex    "Single-use, rotate on every refresh."
```

### 3.3 Escalation

```text
Alex   --ESCALATION--> human   "Blocked: no access to the auth provider's sandbox credentials."
```

## 4. Protocol Conventions

1. **Stay in natural language.** The body is how knowledge transfers; do not smuggle the real content into `metadata`.
2. **One intent per message.** Pick the `MessageType` that matches the dominant purpose.
3. **Keep threads coherent.** Reply within the same `thread_id` so the conversation can be replayed.
4. **Be explicit on handoff.** A `COMPLETION_REPORT` should always state both *what was done* and *what to watch out for*.
5. **Escalate, don't guess.** When blocked or genuinely unsure, send `CLARIFICATION_REQUEST` or `ESCALATION` rather than fabricating.

## 5. Observability

Because every capability is a message, the entire collaboration is observable:

- `MessageBus.poll(agent_id)` — an agent's unread inbox.
- `MessageBus.get_thread(thread_id)` — replay a full conversation.
- `agentmesh watch` — live, color-coded stream of all messages by type.
