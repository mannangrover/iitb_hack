@echo off
REM Service lookup utility for debugging port issues

netstat -ano | findstr :8000
