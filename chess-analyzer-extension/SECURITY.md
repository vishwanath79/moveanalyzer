# Security Overview - Chess Game Analyzer Extension

## Extension Security Features

1. **Limited Permissions**
- No special permissions required
- Only needs network access to specific domains
- No access to sensitive browser data
- No background scripts
- No file system access

2. **API Endpoint Security**
- Uses HTTPS for all API calls
- Communicates only with two whitelisted domains:
  ```json
  "host_permissions": [
    "https://api.chess.com/*",
    "https://chessmover-625329947111.us-central1.run.app/*"
  ]
  ```
- No ability to make requests to unauthorized domains

3. **Data Handling**
- Processes only public chess.com game data
- No personal user data collection
- No storage of game analysis results
- All analysis happens server-side
- No tracking or analytics

4. **Code Transparency**
- Open source code
- Clear documentation
- No obfuscated code
- No third-party libraries
- Minimal dependencies

5. **User Privacy**
- Only analyzes publicly available chess games
- No login required
- No personal information collected
- No cookies used
- No user tracking

6. **Server Security**
- Backend hosted on Google Cloud Run
- Industry-standard security practices
- Regular security updates
- HTTPS encryption
- Rate limiting implemented

## Risk Assessment
- No access to sensitive browser data
- No collection of personal information
- No background processes
- No file system access
- Limited network access to specific domains
- Clear user interface with explicit actions

## Compliance
- Follows Chrome Web Store policies
- Adheres to GDPR guidelines
- Transparent privacy policy
- Clear terms of service
- Regular security updates 