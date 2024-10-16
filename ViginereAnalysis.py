# -*- coding: utf-8 -*-
import re
import math

LETTERS = [ "а","б","в","г","д","е","ё","ж","з","и",
            "й","к","л","м","н","о","п","р","с","т",
            "у","ф","х","ц","ч","ш","щ","ъ","ы","ь",
            "э", "ю", "я"
            ]

FREQUENCIES = [ 8.01, 1.59, 4.54, 1.7, 2.98, 8.45, 0.04, 0.94, 1.65, 7.35,
               1.21, 3.49, 4.40, 3.21, 6.70, 10.97, 2.81, 4.73, 5.47, 6.26,
               2.62, 0.26, 0.97, 0.48, 1.44, 0.73, 0.36, 0.04, 1.90, 1.74,
               0.32, 0.64, 2.01 ]

englishLetterFrequencies = dict(zip(LETTERS, FREQUENCIES))

# Find every sequence of letters with a length ranging from minSize to maxSize
# and encode the sequence and how many times it appears in a dict.
def findPatterns(ciphertext, minPatternSize, maxPatternSize, verbose = True):
    patterns = {}

    for i in range(minPatternSize, maxPatternSize + 1):
        for j in range(i, len(ciphertext)):
            
            pattern = ciphertext[j-i:j]

            if pattern not in patterns:
                matches = re.findall(rf'{pattern}', ciphertext)

                if matches and len(matches) > 1:
                    patterns[pattern] = len(matches)

                    if verbose: print("Pattern: ", pattern, " , Hits: ", matches)
                    

    return patterns

# Calculate the probability of every key length given the number of patterns that
# repeat with a frequency that is a product of that length. (Yes I know this is a bad name
# for the function, fight me)
def predictKeyLength(ciphertext, patterns, minKeySize, maxKeySize, verbose = True):

    if len(patterns) == 0:
        raise Exception("No patterns found! Unable to predict key length.")

    distances = {pattern:[] for pattern in patterns.keys()}


    for pattern in distances.keys():
        locations = []

        for i in range(len(pattern), len(ciphertext)):
            if pattern == ciphertext[i - (len(pattern)):i]:
                locations.append(i)
        
        distances[pattern] = [locations[i] - locations[i - 1] for i in range(1, len(locations))]

    #for pattern, distanceList in distances.items():
        #if verbose: print("Pattern: ",pattern," , distances: ",distanceList)

    
    keyLengths = []

    for i in range(minKeySize, maxKeySize + 1):
        totalSuccesses = 0
        totalFailures = 0

        for distanceList in distances.values():
            
            for distance in distanceList:
                if distance % i == 0:
                    totalSuccesses += 1
                else:
                    totalFailures += 1

        total = totalSuccesses + totalFailures

        keyLengths.append((i, totalSuccesses / total, totalFailures / total))

    keyLengths.sort(key = lambda x: x[2])

    for keyLength in keyLengths:
        if verbose: print("Length: ",keyLength[0]," Successes: ",keyLength[1]," Failures: ",keyLength[2])

    return keyLengths

# Get every character in the ciphertext that was encoded using the position'th letter in the
# key given the key length
def getKeySlice(ciphertext, position, keyLength):
    return "".join([char for i,char in enumerate(ciphertext) if i % keyLength == position])

# Calculate the frequency of every letter in a given piece of text as a percentage of
# the total number of letters.
def calculateLetterFrequency(text):
    letterFrequencies = {letter:0 for letter in LETTERS}
    
    for letter in text:
        letterFrequencies[letter] += 1

    return [freq / len(text) * 100 for freq in letterFrequencies.values()]

# Calculate the RMSE error between the letter frequencies in a given piece of text
# and the letter frequencies in the English language.
def calculateFrequencyFit(text):
    letterFrequencies = calculateLetterFrequency(text)

    errors = [letterFreq - FREQUENCIES[j] for j, letterFreq in enumerate(letterFrequencies)]
    totalError = math.sqrt(sum([error * error for error in errors]) / len(errors))

    return totalError

# Predict the key letter that was used to encode this slice using the frequency of
# the letters in the slice.
def predictKeySliceLetters(keySlice):
    ciphertextLetterFrequencies = calculateLetterFrequency(keySlice)
    letterProbabilities = []

    for i, letter in enumerate(LETTERS):
        errors = [ciphertextFreq - FREQUENCIES[j] for j, ciphertextFreq in enumerate(rotate(ciphertextLetterFrequencies, i))]
        totalError = math.sqrt(sum([error * error for error in errors]) / len(errors))

        letterProbabilities.append((letter, totalError))

    letterProbabilities.sort(key = lambda x: x[1])

    return letterProbabilities

# Decode a vigere cipher given the key.
def decode(ciphertext, key):
    decoded = ""

    keyChar = 0

    for char in ciphertext.lower():
        if char in LETTERS:

            if key[keyChar % len(key)] != "_":
                
                decoded += LETTERS[(LETTERS.index(char) - LETTERS.index(key[keyChar % len(key)])) % len(LETTERS)]
            else:
                decoded += "_"

            keyChar += 1

        else:
            decoded += char

    return decoded

# Encode the plaintext using the key.
def encode(plaintext, key):
    encoded = ""

    keyChar = 0

    for char in plaintext:
        if char in LETTERS:

            if key[keyChar % len(key)] != "_":
                
                encoded += LETTERS[(LETTERS.index(char) + LETTERS.index(key[keyChar % len(key)])) % len(LETTERS)]
            else:
                encoded += "_"

            keyChar += 1

        else:
            encoded += char

    return encoded

# Rotate a list. Takes the last n items in the list and puts them at the front, then shifts
# every other item right by n.
def rotate(seq, n):
    return seq[n:]+seq[:n]

# Predicts key fit by decoding the ciphertext using the key and comparing the resulting
# letter frequencies to those found in English.
def predictKeyFit(ciphertext, key):
    decoded = decode(ciphertext, key)
    return calculateFrequencyFit(decoded)
