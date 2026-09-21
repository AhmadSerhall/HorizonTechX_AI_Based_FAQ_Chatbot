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

## Phase 3 — FAQ Matching Engine

### What we implemented

We created `chatbot.py`, the part of the project that searches the FAQ dataset. It loads the 50 JSON FAQ records, sends every FAQ question through the existing `preprocess_text()` function, converts the processed questions into TF-IDF vectors, and compares a new user query with every FAQ using cosine similarity.

The main matching function, `find_best_match()`, returns a dictionary with the matched FAQ question, answer, category, and similarity score. It does not decide whether the score is good enough yet. That important safety decision belongs to Phase 4.

### Files created or modified

- `chatbot.py` was created for JSON loading, TF-IDF vectorization, cosine similarity, and selecting the highest-scoring FAQ.
- `explication.md` was updated with this Phase 3 section.

`preprocess.py` was reused without copying or changing its NLP logic. `data/faqs.json` was read without modification. `app.py` remains the original Streamlit starter because the chat interface is Phase 5 work.

### The functions in `chatbot.py`

- `load_faqs()` opens `data/faqs.json` and returns the FAQ list.
- `build_faq_vectorizer(faqs)` extracts FAQ questions, preprocesses them with the imported `preprocess_text()`, creates a TF-IDF vectorizer, and fits it to all processed FAQ questions.
- `find_best_match(user_query, faqs, vectorizer, faq_vectors)` preprocesses one user query, compares it against the FAQ vectors, and returns details about the best match.
- `print_match_result(user_query, result)` prints an understandable result for manual testing. It is not the future Streamlit interface.

### What TF-IDF means

**TF-IDF** is short for **Term Frequency–Inverse Document Frequency**. It is a way to turn text into numbers while giving more attention to words that help distinguish one FAQ from another.

**TF, or Term Frequency**, asks: “How much does this word appear in this particular question?” A word that appears in a question is part of that question's representation. In larger documents, repeating a word can increase its TF importance.

**IDF, or Inverse Document Frequency**, asks: “How common is this word across all FAQ questions?” A word appearing in almost every question is less helpful for telling questions apart. A more distinctive word, such as `certificate`, `receipt`, or `browser`, is generally more useful for matching because it appears in fewer FAQ questions.

Together, TF-IDF gives each word a numeric weight. The result is not a human-language meaning; it is a useful numeric description based on the words present in the dataset.

### What a vector is in this project

A **vector** is an ordered list of numbers. After the vectorizer reads all 50 processed FAQ questions, it builds a vocabulary of 93 distinct useful words. Each question then becomes a vector with 93 positions—one position per vocabulary word.

For a simple imaginary vocabulary such as `[certificate, course, password]`, the processed question `download certificate` might become a list like `[0.8, 0.0, 0.0]`. The real project has more words and uses TF-IDF weights, but the idea is the same: every number represents the importance of one vocabulary word in that question. This lets the computer compare questions numerically.

### What `TfidfVectorizer` does

`TfidfVectorizer` is a scikit-learn class. We create one object with `TfidfVectorizer()`. It learns the FAQ vocabulary, calculates TF-IDF weights, and creates a matrix of FAQ vectors.

The object is named `vectorizer` in the code. The resulting `faq_vectors` value is a matrix: a table-like collection where each row represents one FAQ question and each column represents one vocabulary word. During validation, it had the shape `(50, 93)`, meaning 50 FAQ-vector rows and 93 word-feature columns.

### What “fit” and “transform” mean

**Fit** means learning from a collection of data. Here, `vectorizer.fit_transform(processed_questions)` learns the vocabulary and IDF weights from all processed FAQ questions. It also immediately creates their vectors. This combined operation is why it is called `fit_transform`.

**Transform** means applying what has already been learned to new text. `vectorizer.transform([processed_query])` converts a user query into a vector using the existing FAQ vocabulary and existing IDF weights. It does not learn a new vocabulary from the user query.

The FAQ questions and the user query must use the **same fitted vectorizer**. If we fitted a separate vectorizer for the query, its columns could refer to different words or use different weights. The vectors would no longer have a shared meaning, so comparing them would be invalid.

### Cosine similarity and selecting the best FAQ

`cosine_similarity()` compares the direction of two vectors. In this project, it estimates how similar the useful word content of a user query is to the useful word content of each FAQ question.

- A score closer to `1` means the vectors point in very similar directions, so the text is more similar.
- A score closer to `0` means there is little useful word overlap, so the text is less similar.

The function returns one score for each of the 50 FAQ questions. `similarity_scores.argmax()` finds the index of the largest score. Python lists use the same zero-based ordering, so that index points directly to the corresponding FAQ dictionary. The code then takes the `question`, `answer`, and `category` from that dictionary.

### Important imports and Python concepts

- `import json` gives Python the tools to read the FAQ JSON file.
- `from pathlib import Path` supplies `Path`, which creates a reliable path to `data/faqs.json` relative to `chatbot.py`. This works even when the command is run from a different folder.
- `from preprocess import preprocess_text` imports the existing Phase 2 function rather than duplicating NLP code. Both FAQs and user queries therefore receive exactly the same preprocessing.
- `from sklearn.feature_extraction.text import TfidfVectorizer` imports the scikit-learn vectorizer.
- `from sklearn.metrics.pairwise import cosine_similarity` imports the similarity function.
- `with open(...) as file:` opens the JSON file safely and closes it automatically after Python finishes reading it.
- A list comprehension, `[faq["question"] for faq in faqs]`, collects the `question` value from every FAQ dictionary.
- `float(...)` changes the score into a regular Python decimal number, which is simpler to print and later display in Streamlit.
- `if __name__ == "__main__":` runs the three manual test queries only when `chatbot.py` is run directly. Importing its functions later will not run those demonstrations automatically.

### Complete Phase 3 data flow

```text
Raw FAQ questions from data/faqs.json
    ↓
preprocess_text()
    ↓
Processed FAQ questions
    ↓
TfidfVectorizer.fit_transform()
    ↓
FAQ vectors

User query
    ↓
preprocess_text()
    ↓
TfidfVectorizer.transform()
    ↓
Query vector
    ↓
cosine_similarity() against all FAQ vectors
    ↓
50 similarity scores
    ↓
Highest score and its index
    ↓
Corresponding FAQ question, answer, and category
```

### Actual Phase 3 tests

Running `python chatbot.py` loaded and vectorized all 50 FAQ questions. The fitted vocabulary contained 93 word features.

| User query | Best matched FAQ | Category | Score |
| --- | --- | --- | --- |
| `How do I download my certificate?` | `How do I download my certificate?` | Certificates | 1.00 |
| `Can I study using my phone?` | `Can I learn from my mobile phone?` | Courses | 0.60 |
| `certificate after course` | `How do I download my certificate?` | Certificates | 0.57 |

The first test gets `1.00` because, after preprocessing, its wording is the same as the FAQ question. The second uses different wording—`study` instead of `learn` and `phone` instead of `mobile phone`—but it still shares the important word `phone`, so the mobile-learning FAQ is its best match. The third shows that TF-IDF uses the word weights and available overlap; it selected the certificate-download FAQ as the highest-scoring certificate-related question.

### How to test Phase 3 manually

Run the matching demonstration from the project folder:

```powershell
.\venv\Scripts\python.exe chatbot.py
```

You should see `Loaded and vectorized 50 FAQ questions.`, the vocabulary size, and details for all three test queries.

To test the reusable matching function yourself:

```powershell
.\venv\Scripts\python.exe -c "from chatbot import load_faqs, build_faq_vectorizer, find_best_match; faqs = load_faqs(); vectorizer, faq_vectors, _ = build_faq_vectorizer(faqs); print(find_best_match('How can I reset my password?', faqs, vectorizer, faq_vectors))"
```

### Current limitation: every query receives a match

At this stage, the program always returns the FAQ with the largest score, even if every score is poor. For example, an unrelated question might still be paired with the least-unrelated FAQ. A largest score only means “best among this dataset”; it does not automatically mean “good enough.”

Phase 4 will add a confidence threshold. When the best score is below that threshold, the chatbot will return a helpful fallback response instead of a misleading FAQ answer. Phase 4 will also handle empty queries cleanly.

### What the next phase will do

Phase 4 will improve the response logic around this matching engine. It will add the confidence threshold, fallback response, empty-query handling, a clean response structure, and tests for exact, paraphrased, short, unrelated, and empty questions. It will not build the Streamlit UI yet.
