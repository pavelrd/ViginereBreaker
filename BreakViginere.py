# -*- coding: utf-8 -*-
from ViginereAnalysis import *

with open("Ciphertext.txt", mode="r", encoding="utf-8") as ciphertext:
    text = ciphertext.read()

    cleanText = re.sub(r"[^а-яА-Я]+", '', text).lower()
    print(text)
    
    patterns = findPatterns(cleanText, 2, 25)
    keyLengthPredictions = predictKeyLength(cleanText, patterns, 2, 25)

    for prediction in keyLengthPredictions:
        key = []

        for position in range(prediction[0]):
            key.append(predictKeySliceLetters(getKeySlice(cleanText, position, prediction[0]))[0][0])

        key = "".join(key)
        print("\n\n\n")
        print("KEY FIT: ", predictKeyFit(cleanText, key), "WITH KEY: ",key)

        print(decode(text, key))

        input("press any key to continue...")
