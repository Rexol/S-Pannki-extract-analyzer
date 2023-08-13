# S-Pankki extract analyzer

## About

Simple script that helpes analysing the S-Pankki account extract in .csv format. It requires manual categorization of the data, but then it remembers the category based on the recipient name field ("Saajan nimi") which works for the most of my expenses.

```bash
python3 expenseanalyser.py export.csv
```

## Why

I wanted to automate expences analysis, since S-Pankki don't yet have automatic statistics embedded into their app. And I am to lazy to duplicate each transaction in a speciall app.

## How

I have been trying to use Chat gpt for it, but it started forgeting the context on the stage, when I still wasn't satisfied with the functionality. If interested, you can see the versions of the script in the `chatgpt/` folder. Need to say that chatgpt writes quite nice code to start with, but it is difficult to get final version from it :pizza:. May be it was worth to ask for implementation of tests first, and then feed it with the testcases :)

## Future?

I will maintain this script till the condition I am satisfied with (or S-Pankki add this statistics into their app). Current version needs:
- Refactoring
- Fixing functionality implemented by chatgpt
- Tests
- Added configurability, so it works not only with the S-Pankki extracts
- Add simple Logistic regression model (and non simple language model) to make classification process even easier
- Alternatively, create a database of the common places where people do spent their money
