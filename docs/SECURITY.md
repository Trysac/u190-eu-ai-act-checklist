# Security

## Threat Model

- **Defended**: 
  - **Denial of Service**: `load_answers` enforces a strict 65,536 byte limit on input size to prevent memory exhaustion.
  - **Log Injection / Information Disclosure**: Error messages sanitize input by truncating unknown keys or invalid values to 50 characters.
- **Not Defended**:
  - **Logical Accuracy**: This tool does not substitute for legal counsel; the user is responsible for ensuring the input answers correctly reflect their system's architecture.