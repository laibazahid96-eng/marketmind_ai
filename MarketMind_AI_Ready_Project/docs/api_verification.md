# API verification

Build date: 2026-09-06.

The assignment requires current API patterns to be checked rather than copied from old material. This implementation uses the official OpenAI Python SDK and the Responses API surface.

Verified concepts:
- Responses API is the current response surface used by the project.
- Function tools are passed as structured function definitions.
- Usage metadata is read from the response for token accounting.
- The application uses a bounded retry policy and does not expose API credentials in the repository.

Model configuration is controlled by `OPENAI_MODEL`; the default is `gpt-5.6-luna` and can be changed without editing code.
