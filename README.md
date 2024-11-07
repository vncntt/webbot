# Canvas HW Automation for a class

A Python script that automates brute force finding correct answers for Canvas HW and submitting them. Really using the infinite HW retries.

## Overview

This script automates several steps in the Canvas quiz-taking process:
1. Captures the quiz HTML structure
2. Parses questions and possible answers
3. Systematically tries answers to find correct ones
4. Submits the quiz with all correct answers

## Packages:
  ```bash
  pip install selenium beautifulsoup4 python-dotenv
  ```

## Setup

1. Create a `.env` file in the project directory with your Canvas credentials:

```
CANVAS_USERNAME=your_username
CANVAS_PASSWORD=your_password
```

## How It Works

1. **Quiz Source Capture**
   - Logs into Canvas using provided credentials
   - Navigates to quiz URL
   - Saves quiz HTML structure

2. **Structure Parsing**
   - Parses HTML to identify questions and answers
   - Creates JSON structure of quiz content

3. **Answer Finding**
   - Tries each answer option
   - Records correct answers when found
   - Saves progress to resume if interrupted

4. **Final Submission**
   - Submits quiz with all correct answers
   - Confirms submission

## Directory Structure

For each quiz, creates a directory `quiz_[ID]` containing:
- `quiz_source.html`: Raw quiz HTML
- `quiz_structure.json`: Parsed quiz structure
- `answers.txt`: Found correct answers

## Notes
- Can resume from where it left off if interrupted
- Saves correct answers as they're found
- Skips already-completed steps
- Uses one browser instance for entire process
- Will absolutely require adjustments for different quiz types

## Flaws
- Will not work for select multiple questions, fill-in-the-blank questions
- Will not work for slightly different HTML structures
- Uses the most basic brute force method of finding answers