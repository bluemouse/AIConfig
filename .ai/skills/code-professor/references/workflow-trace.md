# End-to-end workflow trace

Use this document to explain how an event, request, command, frame, job, message, asset, or data item travels through the system.

## Default structure

# Workflow trace: [workflow]

## 1. Trigger and final effect

Define the starting event, the observable outcome, and the boundaries of the trace.

## 2. Sequence overview

Give a numbered summary of the stages. Include a compact sequence or data-flow diagram when useful.

## 3. Detailed trace

For every stage, state:

1. entry condition and caller
2. function, method, handler, or process entered
3. important inputs and state read
4. validation and branching decisions
5. transformation or side effect
6. output and next consumer
7. error, cancellation, retry, or cleanup path

Cite every stage with path:line evidence. At **overview** depth, trace only the happy path and name error branches without full detail.

## 4. Data model and transformations

Describe the data shape at important boundaries, including serialization, normalization, caching, batching, copying, or ownership transfer.

## 5. Cross-cutting behavior

Cover relevant configuration, feature flags, logging, metrics, security checks, resource management, and platform branches.

## 6. Concurrency and timing

Explain scheduling, queues, callbacks, thread or process hops, synchronization, ordering assumptions, and backpressure.

## 7. Validation performed

List commands, tests, traces, or controlled experiments and their outcomes.

## 8. Failure scenarios and debugging entry points

Identify likely breakpoints, logs, state probes, and tests for each major stage.

## 9. Optional opportunities

Suggest simplifications, observability improvements, extension points, or candidate fixes without confusing them with current behavior.
