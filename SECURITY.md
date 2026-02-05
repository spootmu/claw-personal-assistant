# Security Policy for Claw Personal Assistant

## Data Protection & Privacy

This project follows strict data protection and privacy principles:

1. **No Hardcoded Credentials**: The project does not contain any hardcoded API keys, tokens, passwords, or other sensitive information.

2. **Secure Configuration**: All sensitive configuration values should be provided at runtime through secure means, never stored in the codebase.

3. **Privacy by Design**: The system is designed to operate without storing or transmitting personal or sensitive user data.

4. **Environment Variables**: Any required credentials should be passed through environment variables or secure configuration files not stored in the repository.

## Best Practices

- Never commit sensitive data to the repository
- Use `.env` files or environment variables for configuration
- Regular security audits of dependencies
- Input validation and sanitization
- Secure communication protocols

## Reporting Security Issues

If you discover a security vulnerability, please contact the project maintainers directly.