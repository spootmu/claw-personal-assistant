# Claw Personal Assistant - Project Configuration

## Project Governance

### Autonomy Level
- This project operates with high autonomy under the direction of the AI assistant
- The AI assistant has full authority to make technical decisions and implement changes
- Only major architectural changes or security-related decisions require explicit approval

### Development Approach
- Rapid iteration based on community insights and best practices
- Emphasis on modularity and maintainability
- Three-tier memory architecture (hot/warm/cold) for data management
- Security-first approach with no hardcoded credentials

## Technical Architecture

### Storage Strategy
- **Hot Storage**: JSON files for immediate access and temporary data
- **Warm Storage**: SQLite database for structured data and history
- **Cold Storage**: Archive files for backup and long-term retention

### Core Components
1. **Main Controller** - Orchestrates operations
2. **Task Engine** - Manages task execution
3. **Memory System** - Handles learning and retention
4. **Community Integration** - Processes external insights
5. **Database Manager** - Structured data storage

## Operation

### Running Mode
- The project is designed to run autonomously by the AI assistant
- No manual intervention required for regular operation
- Automatic monitoring and self-improvement based on community insights

### Security Guidelines
- No sensitive information stored in codebase
- All credentials handled through environment variables
- Regular security audits of dependencies
- Input validation and sanitization for all data processing