from zhconv import convert
from opencc import OpenCC

import langdetect
from langdetect import DetectorFactory

import re
import langid

import sys
import os

def ConvertZhsToZht_opencc(target):
    if isinstance(target, str):
        cc = OpenCC('s2t')
        DetectorFactory.seed = 0
        to_check = re.sub("[a-zA-Z0-9\n\./_<>:;]","",target)
        print(to_check)
        if langdetect.detect(to_check) == "zh-cn":
            converted = cc.convert(target)
            print(converted)
            return converted
        else:
            print("Not zhs, lang is %s"%langdetect.detect(to_check))
            print(langdetect.detect_langs(to_check))
            return ""
    else:
        print("input is not string")
        return ""

def ConvertZhsToZht_langid(target):
    if isinstance(target, str):
        cc = OpenCC('s2t')
        DetectorFactory.seed = 0
        to_check = re.sub("[a-zA-Z0-9\n\./_<>:;(),\{\}\[\]]\s","",target)
        #print("check string = %s>"%to_check)

        langid.set_languages(['en','zh','ja'])
        if langid.classify(to_check)[0] == "zh":
            converted = cc.convert(target)
            #print(converted)
            return converted
        else:
            #print("Not zh, lang is %s"%langid.classify(to_check)[0])
            return target
    else:
        #print("input is not string")
        return target

def TraversalDict(input_dict):
    if isinstance(input_dict, dict):
        for key in input_dict:
            if isinstance(input_dict[key], dict):
                TraversalDict(input_dict[key])
            else:
                print("key = %s, Value = %s"%(key, input_dict[key]))
                input_dict[key] = ConvertZhsToZht_langid(input_dict[key])

def Convert(file, update_to_same_file):
    file_data = ""
    count_line = 0
    total_line = GetFileLine(file)
    print('Translate %s ...'%file)
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            count_line += 1

            if not IsAscii(line):
                substring = line.split("\"")
                for partstring in substring:
                    if not IsAscii(partstring):
                        converstring = ConvertZhsToZht_langid(partstring)
                        if partstring != converstring:
                            line = line.replace(partstring, converstring)
            file_data += line

            if total_line != 0:
                process = int((count_line / total_line) * 100)
                print("\r", end="")
                print("Process: {}%: ".format(process), "▓" * (process // 2), end="")
                sys.stdout.flush()

    new_file = ""
    if update_to_same_file:
        new_file = file
    else:
        new_file = "Update_" + file
            
    with open(new_file, "w", encoding="utf-8") as f:
        f.write(file_data)
    print("\r", end="")
    print('Translate to %s Done !!'%new_file)

def IsAscii(s):
    return all(ord(c) < 128 for c in s)

def GetFileLine(target):
    return sum(1 for line in open(target, encoding="utf-8"))

def FileTraversal(root_path):
    path = os.walk(root_path)
    for root, directories, files in path:
        #for directory in directories:
        #    print(directory)
        for file in files:
            if file.find(".json") != -1 or file.find(".js") != -1:
                Convert(file, True)


if __name__ == '__main__':
    FileTraversal(".")