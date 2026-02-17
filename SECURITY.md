# Security Policy

## Supported Versions

We actively maintain and provide security updates for the following versions of Investory:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Investory seriously. If you discover a security vulnerability, please follow these guidelines:

### Please Do Not

- **Do not** open a public GitHub issue for security vulnerabilities
- **Do not** disclose the vulnerability publicly until it has been addressed
- **Do not** exploit the vulnerability beyond what is necessary to demonstrate it

### Please Do

1. **Report Privately**
   - Use GitHub's Private Vulnerability Reporting feature (preferred)
   - Or email: security@example.com (replace with your contact)
   - Include detailed information about the vulnerability

2. **Include in Your Report**
   - Type of vulnerability
   - Full paths of affected source files
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the vulnerability and potential attack scenarios

3. **Allow Time for Response**
   - We will acknowledge receipt within 72 hours
   - We aim to provide an initial assessment within 1 week
   - We aim to patch critical vulnerabilities within 14 days

## Security Update Process

When we receive a security vulnerability report:

1. **Acknowledgment**: We confirm receipt and begin investigation (within 72 hours)
2. **Assessment**: We assess the impact and severity of the vulnerability
3. **Development**: We develop and test a fix
4. **Disclosure**: We coordinate disclosure timing with the reporter
5. **Release**: We release a security patch and publish a security advisory
6. **Credit**: We credit the reporter in the security advisory (unless they prefer to remain anonymous)

## Security Best Practices

### For Users

When deploying Investory in production:

1. **Environment Variables**
   - Never commit `.env` files to version control
   - Use strong, unique passwords for database credentials
   - Rotate API keys periodically
   - Use environment-specific configurations

2. **Database Security**
   - Use strong PostgreSQL passwords
   - Restrict database network access
   - Enable SSL/TLS for database connections in production
   - Regular backups with encrypted storage

3. **API Keys**
   - Protect your Alpha Vantage API key
   - Monitor API usage for anomalies
   - Use rate limiting in production
   - Consider API key rotation policies

4. **Network Security**
   - Use HTTPS in production (configure Nginx with SSL/TLS)
   - Implement firewall rules to restrict access
   - Use reverse proxy for additional security
   - Enable CORS only for trusted origins

5. **Docker Security**
   - Keep Docker and images up to date
   - Use official base images
   - Scan images for vulnerabilities
   - Run containers with minimal privileges
   - Use Docker secrets for sensitive data

6. **Updates**
   - Keep Investory updated to the latest version
   - Monitor security advisories
   - Subscribe to release notifications
   - Test updates in staging before production

### For Contributors

When contributing to Investory:

1. **Code Review**
   - All code changes require review before merging
   - Security-sensitive changes require additional scrutiny

2. **Dependencies**
   - Keep dependencies updated
   - Review dependency security advisories
   - Use `pip audit` and `npm audit` regularly

3. **Secure Coding**
   - Validate and sanitize all user inputs
   - Use parameterized queries (SQLAlchemy ORM handles this)
   - Avoid exposing sensitive data in logs or error messages
   - Follow OWASP Top 10 guidelines

4. **Authentication & Authorization**
   - Plan for proper authentication in future versions
   - Implement least privilege access controls
   - Secure session management

## Known Security Considerations

### Current Limitations

1. **No Authentication**: Version 1.0 does not include user authentication
   - Suitable for personal/internal use
   - Should not be exposed to public internet without additional authentication layer
   - Authentication is planned for v1.1

2. **API Rate Limiting**: Basic rate limiting relies on Alpha Vantage's limits
   - Consider implementing application-level rate limiting for production
   - Monitor for abuse

3. **Input Validation**: Stock symbols are validated but additional validation layers can be added
   - Current validation sufficient for typical use
   - Additional sanitization in development for v1.1

### Future Security Enhancements

Planned security improvements for future versions:

- **v1.1**: JWT-based authentication and authorization
- **v1.1**: Role-based access control (RBAC)
- **v1.2**: API rate limiting and throttling
- **v1.2**: Enhanced input validation and sanitization
- **v1.3**: Audit logging for security events
- **v1.3**: Two-factor authentication (2FA) support

## Security Hall of Fame

We recognize and thank security researchers who responsibly disclose vulnerabilities:

- *No vulnerabilities reported yet*

---

## Questions?

If you have questions about security practices or need clarification on any security matters, please:

- Check our documentation in the `/docs` folder
- Open a discussion on GitHub (for non-sensitive topics)
- Email security@example.com (for sensitive security questions)

Thank you for helping keep Investory and its users secure!
