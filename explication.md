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

## Phase 2 — NLP Preprocessing

### What we implemented

We created `preprocess.py`, a reusable Python module that converts a raw English question into a simpler, consistent form. Its main function is `preprocess_text(text)`. It applies this pipeline:

```text
raw text → lowercase → tokens → alphabetic tokens → no stopwords → lemmas → processed text
```

The module also contains two learning helpers. `get_preprocessing_steps(text)` returns each intermediate stage in a dictionary, while `print_preprocessing_steps(text)` prints those stages clearly. These helpers make the process visible while we are learning and testing. In Phase 3, the matching engine will only need `preprocess_text()`.

No TF-IDF vectorizer, cosine similarity calculation, FAQ loading code, matching logic, or chatbot interface was added in this phase.

### Why NLP preprocessing matters

**Natural Language Processing (NLP)** is the area of programming that helps computers work with human language. People can ask the same question in several ways: “How do I download certificates?”, “download my certificate”, or “Where is my certificate download?” A computer needs a more consistent representation before it can compare those questions.

Raw text contains differences that often do not change the meaning for our FAQ matcher: uppercase letters, punctuation, frequent helper words, and plural word forms. Preprocessing reduces some of that noise. It does not make the chatbot understand language like a person; it prepares useful words for the TF-IDF and cosine-similarity method we will add later.

### Files created or modified

- `preprocess.py` was created. It owns NLTK setup and reusable text preprocessing.
- `explication.md` was updated with this Phase 2 section.

`data/faqs.json` was reviewed but not changed. Its `question` strings are compatible with `preprocess_text()`. `app.py` remains the original Streamlit starter, and `chatbot.py` does not exist yet because it belongs to Phase 3.

### NLTK and its required resources

**NLTK** stands for Natural Language Toolkit. It is a Python library with tools and language data that are useful when learning NLP.

Installing the `nltk` Python package is not enough for every feature. Tokenization, English stopwords, and WordNet lemmatization also use separate data packages. `ensure_nltk_resources()` checks whether each one exists and quietly downloads it only if it is missing:

- `punkt` and `punkt_tab`: language data used by NLTK tokenization in the installed NLTK version.
- `stopwords`: the English stopword list.
- `wordnet`: the lexical database used by the lemmatizer.
- `omw-1.4`: extra WordNet data used alongside WordNet.

This check happens when `preprocess.py` is imported or run. Normally it is a quick local check after the first download. The first run needs an internet connection if those resources are not already installed.

### What each import does

- `import nltk` gives the file access to NLTK itself, including its resource finder and downloader.
- `from nltk.corpus import stopwords` imports NLTK's collection of common words.
- `from nltk.stem import WordNetLemmatizer` imports the lemmatizer class. The program creates one reusable object named `LEMMATIZER` from it.
- `from nltk.tokenize import word_tokenize` imports the function that splits a sentence into tokens.

An **import** lets one Python file use code written in another package. The `from ... import ...` form brings in only the named tool, so we can write `word_tokenize(...)` instead of a longer package path.

### How `preprocess_text()` works

`preprocess_text(text)` calls `get_preprocessing_steps(text)` and joins its final list of words with spaces. The result is a string, which is convenient for the TF-IDF vectorizer in Phase 3.

Inside the pipeline:

1. It checks that `text` is a string. A **string** is text in Python. If a number, list, or other type is passed by mistake, Python raises a clear `TypeError` instead of producing a confusing result.
2. `text.lower()` makes every letter lowercase. Therefore `Course`, `COURSE`, and `course` are treated as the same word.
3. `word_tokenize()` performs **tokenization**: it splits text into small pieces called **tokens**. Words and punctuation become separate tokens. A computer can filter and compare a list of tokens more easily than one long sentence.
4. The list comprehension `token for token in tokens if token.isalpha()` keeps only alphabetic tokens. It removes punctuation such as `?` and `,`, plus numbers or symbols. `isalpha()` is a string method that is true only for letters.
5. Another list comprehension removes English **stopwords**. Stopwords are very common words that usually add little topic information when comparing FAQ questions, such as `the`, `is`, `and`, `my`, `do`, and `can`.
6. `LEMMATIZER.lemmatize(token)` changes words to a basic dictionary form called a **lemma**. For example, `courses` becomes `course`, `passwords` becomes `password`, and `learners` becomes `learner`. This simple beginner-friendly use focuses especially on common noun forms; it does not yet add the extra complexity of part-of-speech tagging.
7. `" ".join(...)` combines the final word list back into one space-separated processed string.

### A complete transformation example

When the module is run, its detailed example is:

```text
Original sentence: How do I reset my passwords for the courses?
↓
Lowercase: how do i reset my passwords for the courses?
↓
Tokenization: ['how', 'do', 'i', 'reset', 'my', 'passwords', 'for', 'the', 'courses', '?']
↓
Remove punctuation/non-alphabetic tokens: ['how', 'do', 'i', 'reset', 'my', 'passwords', 'for', 'the', 'courses']
↓
Remove stopwords: ['reset', 'passwords', 'courses']
↓
Lemmatization: ['reset', 'password', 'course']
↓
Final processed result: reset password course
```

The raw sentence is easy for a person to read. The processed result is shorter and intentionally loses grammar words and punctuation so it keeps the terms that are most useful for later FAQ matching.

### Important Python syntax used

- **Function definitions:** `def function_name(...):` defines reusable instructions. Parameters, such as `text`, are input values supplied when a function is called.
- **Return:** `return` sends a result back to the code that called the function. `get_preprocessing_steps()` returns a dictionary; `preprocess_text()` returns a string.
- **Dictionary:** the preprocessing-steps dictionary gives each intermediate result a descriptive key, such as `tokens` or `lemmatized_tokens`.
- **List comprehension:** `[item for item in items if condition]` is a compact loop that builds a new list. Here it filters unwanted tokens.
- **Set:** `set(stopwords.words("english"))` stores stopwords in a set. Sets are helpful for fast “is this word present?” checks.
- **`if __name__ == "__main__"`:** every Python file has a `__name__` value. This condition is true only when this file is run directly with `python preprocess.py`. It lets us run demonstrations without printing them when Phase 3 imports the module.
- **f-string:** text such as `f"...{value}..."` inserts a variable value into a printable message. The demonstration function uses f-strings to label each stage.

### How data moves through preprocessing

```text
User or FAQ question (raw string)
    ↓
preprocess_text()
    ↓ lowercase, tokenize, filter, remove stopwords, lemmatize
Processed string, for example: "reset password course"
    ↓ Phase 3
TF-IDF vectorization and cosine-similarity comparison
```

In Phase 3, the same preprocessing function must be used for both the FAQ questions from `data/faqs.json` and a new user question. That consistency lets the vectorizer compare like with like.

### How to test Phase 2 manually

Run this from the project folder while the virtual environment is available:

```powershell
.\venv\Scripts\python.exe preprocess.py
```

The first run may download the missing NLTK resources. You should then see the detailed transformation and three additional FAQ-related examples.

You can also test the primary function directly:

```powershell
.\venv\Scripts\python.exe -c "from preprocess import preprocess_text; print(preprocess_text('Can I download course videos on my mobile phone?'))"
```

An expected result is `download course video mobile phone`.

### Common errors you might encounter

- **`LookupError` mentioning an NLTK resource:** make sure you have an internet connection for the first run, then run `preprocess.py` again. The resource checker should download the needed data automatically.
- **`ModuleNotFoundError: No module named 'nltk'`:** use the project virtual environment, or install the dependencies listed in `requirements.txt` into the environment you are using.
- **`TypeError: text must be a string`:** pass text in quotation marks, not a number, dictionary, or list.
- **An empty result for a very short question:** a question made entirely of stopwords, such as `"How do I?"`, has no useful topic words after filtering. Phase 4 will handle empty user input and weak matches safely.

### What the next phase will do

Phase 3 will create `chatbot.py`. It will load `data/faqs.json`, preprocess every FAQ question with `preprocess_text()`, turn the processed questions into TF-IDF vectors, compare a processed user query with cosine similarity, and select the best matching FAQ. It will not build the full Streamlit chat UI yet.
