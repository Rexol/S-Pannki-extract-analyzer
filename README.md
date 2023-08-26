# S-Pankki Extract Analyzer

## Description

The S-Pankki Extract Analyzer is a straightforward script designed to assist in the analysis of S-Pankki account extracts provided in .csv format. The script facilitates manual categorization of the data, while also incorporating a memory feature that associates categories with recipient names ("Saajan nimi"). This proves effective for categorizing the majority of my expenses.


## Usage

Execute the script using the following command:

```bash
python3 expense_analyzer.py export.csv
```


## Motivation

This project emerged from the need to automate expense analysis, as S-Pankki's current application lacks built-in automatic statistical functionality. The avoidance of duplicating each transaction in a dedicated application served as a driving force behind this automation effort.


## Methodology

Initially, I experimented with utilizing ChatGPT for this task. However, the model exhibited a tendency to lose context during development stages, hindering the attainment of desired functionality. Interested individuals can access various script versions within the chatgpt/ folder. It is noteworthy that ChatGPT generates commendable initial code, although refining it into a final version posed challenges. Perhaps it would have been prudent to request test case implementations before soliciting code generation from the model.


## Future Prospects

I will continue refining this script until I achieve a level of satisfaction or until S-Pankki integrates statistical features into their application. The current version necessitates the following enhancements:

- Comprehensive refactoring
- Implementation of testing procedures
- Enhanced configurability to accommodate not just S-Pankki extracts
- Introduction of a basic Logistic Regression model (and potentially a more complex language model) to simplify the classification process
- Alternatively, establishment of a database cataloging common expenditure locations