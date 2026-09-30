# Practice 2 — Flight Customer Support Agent

This implementation keeps the original Practice 2 flow and adds:

- Bounded agent loop with configurable maximum iterations/tool calls.
- Basic input and tool-call guardrails.
- Customer-isolated JSON memory.
- Cache-first booking/flight reads; SQLite is used on cache misses.
- Memory tools: `save_memory` and `retrieve_memory`.
- Cached booking state is updated after seat/meal changes.
- Seat availability is checked before a seat change.
- No customer can read another customer's memory because memory tools require the
  customer identity established by the selected booking.

## Configuration

Environment variables are optional:

```bash
export OPENAI_MODEL=gpt-5.5
export MAX_AGENT_ITERATIONS=8
export MAX_TOOL_CALLS=12
export MAX_INPUT_LENGTH=2000
```

## Run

From this directory:

```bash
python app.py
```

The persistent customer memory/cache is stored under:

```text
practice2/memory/
```

Each customer gets a separate file such as `customer_1.json`.

The booking-reference routing cache is kept separately from customer memory and
contains only the minimum mapping needed to locate a customer's isolated cache.
