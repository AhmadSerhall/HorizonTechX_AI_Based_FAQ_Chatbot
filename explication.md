# HorizonTechX FAQ Chatbot — Learning Notes

This file grows alongside the project. It explains the decisions and concepts behind the code in beginner-friendly language instead of repeating the source code.

## Phase 1 — Project Foundation and FAQ Dataset

### What we implemented

We chose an **online technology-learning platform** named **HorizonTechX Learning Hub** as the chatbot topic. The project now has a structured FAQ dataset containing 50 realistic questions and answers. The FAQ topics include account setup, courses, learning progress, certificates, payments, technical help, community features, and learning paths.

At this stage, the application still only displays the original Streamlit starter page. The chatbot does not yet preprocess text or search the FAQ data. Keeping Phase 1 limited this way makes it easier to understand the foundation before adding NLP.

### Why we implemented a dataset first

An FAQ chatbot needs reliable information before it can answer questions. The dataset is the chatbot's knowledge source: later code will compare what a user writes against the `question` values and return the matching `answer`.

The questions are grouped into categories. Categories are useful for people reading the data and can later be shown in a debug view or interface. The matching engine will initially use the question text itself, not the category alone.

### Files created or modified

- `data/faqs.json` was filled with the 50 FAQ records.
- `explication.md` was created for these learning notes.

The following existing files were intentionally not changed in this phase:

- `app.py` remains the tested Streamlit starter.
- `requirements.txt` already includes NLTK, scikit-learn, and Streamlit.
- `.gitignore` already excludes the virtual environment, Python cache files, and `.env` files.

### Understanding the JSON dataset

JSON means **JavaScript Object Notation**. It is a plain-text format for organizing data. Python can read JSON easily, so it is a good first choice for a small FAQ dataset.

The whole file is a **list**. A list is an ordered collection written between square brackets (`[ ]`). Each item in this list is a **dictionary**, written between curly braces (`{ }`). A dictionary stores named pieces of data as key-value pairs.

Each FAQ dictionary contains four keys:

- `id`: a unique number that identifies the FAQ.
- `category`: a label such as `Courses` or `Technical Support`.
- `question`: the question that the later matching engine will compare with a user's message.
- `answer`: the response the chatbot should show when that FAQ is the best match.

For example, conceptually, one FAQ is a small record: “this question belongs to this category and has this answer.” The quotation marks are important because JSON text values must be strings. Commas separate items, but there is no comma after the final item in a list or dictionary.

### Important Python concepts for this phase

There is no new Python program logic yet, but the next phase will load this data into Python:

- **Import:** an `import` statement lets a Python file use code from a library. Later, Python's built-in `json` module will be imported to read `faqs.json`.
- **Function:** a reusable named block of code. We will create functions so each job, such as preprocessing text or finding an answer, has a clear home.
- **List:** an ordered collection. After loading the JSON file, Python will represent the full FAQ collection as a list.
- **Dictionary:** a collection of named values. Each loaded FAQ will become a dictionary, allowing code such as “get this FAQ's question” or “get this FAQ's answer.”
- **Loop:** a way to repeat work for every item in a list. The matching engine will later loop through all FAQ questions or process them as a collection.

### Data flow at the end of Phase 1

```text
faq author
    ↓ writes structured questions and answers
data/faqs.json
    ↓ will be loaded in Phase 3
Python list of FAQ dictionaries
    ↓ will be searched after NLP processing
chatbot response
```

Right now the first two parts exist. The loading, searching, and response steps will be added in later phases.

### How to test Phase 1

1. Open `data/faqs.json` in your editor.
2. Confirm it contains 50 FAQ objects with `id`, `category`, `question`, and `answer` fields.
3. In the project terminal, run this command to validate the JSON syntax:

   ```powershell
   python -m json.tool data/faqs.json
   ```

   If the command prints formatted JSON and no error, the file is valid.
4. You can still run the existing starter application:

   ```powershell
   streamlit run app.py
   ```

   It should show the original title and message. It will not yet answer questions because that belongs to later phases.

### Common errors you might encounter

- **`JSONDecodeError`:** JSON syntax is invalid. Check for missing commas, extra commas after the final item, missing quotation marks, or mismatched square/curly brackets.
- **File not found:** run commands from the project folder, the one containing `app.py` and the `data` directory.
- **A changed question has no matching answer later:** every FAQ object should keep all four fields, especially `question` and `answer`.
- **Using single quotes in JSON:** JSON requires double quotes around keys and text values.

### What the next phase will do

Phase 2 will create `preprocess.py` and use NLTK to prepare text for matching. It will demonstrate lowercase conversion, tokenization, punctuation removal, stopword removal, and lemmatization with a step-by-step example sentence. No full Streamlit chat interface will be built yet.
