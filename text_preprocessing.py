import re
from datetime import datetime

import pycountry
from nltk.corpus import stopwords, words
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize
from spellchecker import SpellChecker


def get_preprocessed_text_terms(text: str, dataset_name: str) -> list:
    """
    Apply text processing steps of a given text

    Args:
        text: The text you want to process
        dataset_name: The name of the dataset to use. Can be either "technology" or "quora".

    Returns:
        A list of cleansing tokens
    """
    # 1) Tokenizing: extract tokens from the text
    tokens = _get_words_tokenize(text)
    # 2) Lowerization: convert all tokens to lowercase
    lowercase_tokens = _lowercase_tokens(tokens)
    # 3) Cleaning: remove punctuation tokens
    cleaned_tokens = _remove_punctuations(lowercase_tokens)
    # 4) Filtration: remove stop words "if dataset is quora, the question words will not be removed"
    filtered_tokens = _filter_tokens(cleaned_tokens, dataset_name)
    d = _normalize_dates(filtered_tokens)
    c = _normalize_country_names(d)
    # 5) Stemming: stemming the tokens
    stemmed_tokens = _stem_tokens(c)

    return stemmed_tokens


def _get_words_tokenize(text: str) -> list:
    """
      Splitting string to tokens

      Args:
          text: The text you want to tokenize

      Returns:
          A list of extracted tokens
      """

    return word_tokenize(text)


def _spell_check_tokens(tokens: list, query: bool):
    """
    Apply spell checking of a given list of tokens

    Args:
        tokens: The list of token you want to process
        query: True if tokens refer to a search query

    Returns:
        If query => list of corrected tokens
        Else => given list
    """
    if query:
        spell = SpellChecker()

        word_set = set(words.words())

        # Create a list to store the corrected tokens
        corrected_tokens = []

        # Spell check each token
        for token in tokens:
            if token in word_set:
                corrected_tokens.append(token)
            else:
                # Find the highest-ranked suggestion using the spell-checker
                suggestions = spell.candidates(token)
                if suggestions:
                    corrected_tokens.append(spell.correction(token))
                else:
                    corrected_tokens.append(token)

        return corrected_tokens
    else:
        return tokens


def _lowercase_tokens(tokens: list) -> list:
    """
    Apply lowerization of a given list of tokens

    Args:
        tokens: The list of token you want to process

    Returns:
         A list of lowered tokens
    """
    return [token.lower() for token in tokens]


def _remove_punctuations(tokens: list) -> list:
    """
         Remove punctuations from a given list of tokens

          Args:
              tokens: The list of token you want to process

          Returns:
               A list of tokens without punctuations
      """

    tokenizer = RegexpTokenizer(r'\w+')
    non_punctuations_tokens = tokenizer.tokenize(' '.join(tokens))
    return non_punctuations_tokens


def _filter_tokens(tokens: list, dataset_name: str) -> list:
    """
        Remove stop words from a given list of tokens

         Args:
             tokens: The list of token you want to process

         Returns:
            If dataset_name is quora  A list of tokens without stop words except the question words
            Else A list of tokens without stop words
     """
    stop_words = set(stopwords.words('english'))

    question_words = {'what', 'who', 'whom', 'whose', 'which', 'when', 'where', 'why', 'how', 'how much', 'how many',
                      'how long', 'how often', 'how far', 'how old', 'how come'}
    if dataset_name == 'technology':
        filtered_stop_words = stop_words
    else:
        filtered_stop_words = stop_words - question_words

    filtered_tokens = [token for token in tokens if token not in filtered_stop_words]

    return filtered_tokens


def _stem_tokens(tokens: list) -> list:
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return stemmed_tokens


def _normalize_dates(tokens: list) -> list:
    """
    Apply date normalization of a given list of tokens

    Args:
        tokens: The list of token you want to process

    Returns:
        A list of normalized date tokens
    """
    # Define regular expression pattern for valid date strings
    date_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|' \
                   r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})|' \
                   r'(\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{2,4})|' \
                   r'((Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},\s+\d{2,4})|' \
                   r'(\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4})|' \
                   r'((January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{2,4})'

    # Define list of format strings to try when parsing date strings
    format_strings = ['%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y', '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%d %b %Y', '%b %d, %Y',
                      '%d %B %Y', '%B %d, %Y', '%m/%d/%Y', '%m-%d-%Y', '%m.%d.%Y', '%d-%m-%y', '%d/%m/%y', '%d.%m.%y',
                      '%y-%m-%d', '%y/%m/%d', '%y.%m.%d', '%d %b %y', '%b %d, %y',
                      '%d %B %y', '%B %d, %y', '%m/%d/%y', '%m-%d-%y', '%m.%d.%y']

    # Loop through each token and replace valid date strings with normalized date strings
    normalized_tokens = []
    for token in tokens:
        # # Skip tokens that consist of only double quotes or single quotes
        # if token in ['"', "''", '``']:
        #     continue
        # Check if the token matches the date pattern
        matches = re.findall(date_pattern, token)
        if matches:
            # If the token matches the date pattern, try parsing it using each format string in turn
            match = matches[0][0]  # Get the first match in the tuple
            for fmt in format_strings:
                try:
                    date_obj = datetime.strptime(match, fmt)
                    break  # Stop trying format strings when one succeeds
                except ValueError:
                    pass
            else:
                continue  # Skip the token if none of the format strings succeeded
            # Replace the matched date string with the normalized date string
            normalized_date = date_obj.strftime('%Y-%m-%d')
            token = token.replace(match, normalized_date)
        normalized_tokens.append(token)

    return normalized_tokens


def _normalize_country_names(tokens: list) -> list:
    """
    Apply country normalization of a given list of tokens

    Args:
        tokens: The list of token you want to process

    Returns:
        A list of normalized country tokens
    """

    # Create a set of country names for faster lookup
    country_codes = set(country.alpha_3 for country in pycountry.countries)

    # Loop over the tokens and update country names if they match a country name
    for token in tokens.copy():
        if token.upper() in country_codes:
            try:
                country = pycountry.countries.lookup(token.upper())
                tokens.remove(token)
                tokens.append(country.name)
            except LookupError:
                pass

    # Return the updated list of tokens
    return tokens


def _lemmatize_tokens(tokens: list) -> list:
    """
          Lemmatize tokens: Apply a sophisticated algorithm that uses a dictionary-like mapping of words to their base or
          root form. It considers the context of the word and its part of speech to determine the correct base form

           Args:
               tokens: The list of token you want to process

           Returns:
              A list of lemmatized tokens
       """
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return lemmatized_tokens


__all__ = ['get_preprocessed_text_terms']
