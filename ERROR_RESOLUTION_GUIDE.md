# Claw Error Resolution Guide

## Common Error #1: Windows PowerShell && Operator Issue
**Problem**: Command execution failing with "&&" operator syntax error in Windows environment
**Solution**: Use batch files or cmd /c to execute chained commands properly
**Reference**: RUNNING_INSTRUCTIONS.md in claw-personal-assistant project

## Common Error #2: Edit Tool Missing Parameter
**Problem**: Using edit tool without providing the required `oldText` parameter
**Solution**: Always provide both `oldText` (the exact text to be replaced) and `newText` (the replacement text) when using the edit tool
**Example**:
```json
{
  "file_path": "path/to/file.txt",
  "oldText": "exact text to find and replace",
  "newText": "replacement text"
}
```
**Alternative**: Use the `write` tool if you want to completely overwrite a file

## Common Error #3: Unix Commands on Windows
**Problem**: Attempting to use Unix/Linux commands like `df` on Windows system
**Solution**: Use Windows-native alternatives:
- Instead of `df -h`, use `fsutil volume diskfree C:` or `Get-PSDrive`
- Instead of Unix paths with forward slashes, use Windows paths with backslashes
- Use PowerShell cmdlets appropriate for the Windows platform

## Common Error #4: Incorrect Path References
**Problem**: Referencing incorrect paths that don't exist on the system
**Solution**: Always verify path existence before attempting operations
- Use `Test-Path` in PowerShell to check if a path exists
- Be mindful of absolute vs relative paths
- Account for different directory structures on Windows vs Unix systems

## Common Error #5: Forgetting Git Synchronization
**Problem**: Not committing and pushing changes to remote repository regularly
**Solution**: Always commit and push changes after completing significant work
- Use git add . to stage all changes
- Use git commit with descriptive messages to save changes
- Use git push origin main to sync with remote repository
- Make this a standard part of workflow to prevent data loss

## Common Error #6: Privacy and Security Oversight
**Problem**: Accidentally committing sensitive or private information to public repositories
**Solution**: Always review files before committing and maintain proper .gitignore
- Update .gitignore to exclude sensitive files (.env, *.secret, config.json, etc.)
- Never commit files containing passwords, API keys, or personal information
- Use git status to review all staged files before committing
- For privacy files, use local storage instead of version control

## Common Error #7: Storing Credentials in Source Code
**Problem**: Creating files with embedded API keys or credentials in project directories
**Solution**: Never store credentials directly in source files
- Use environment variables for sensitive information
- Implement secure configuration systems instead of hardcoding credentials
- If testing APIs, use temporary files outside the project or secure vaults
- Immediately delete any files containing credentials that were created accidentally

## Key Takeaway
Always check tool parameters carefully before execution to avoid common mistakes that waste resources and cause errors.