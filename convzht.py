# -*- coding: utf-8 -*-
from zhconv import convert
from opencc import OpenCC

import langdetect
from langdetect import DetectorFactory, detect, detect_langs

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
        to_check = re.sub("[a-zA-Z0-9\n\./_<>:;(),\{\}\[\]]\s","",target)
        #print("check string = %s>"%to_check)

        langid.set_languages(['en','zh','ja'])
        if langid.classify(to_check)[0] == "zh":
            cc = OpenCC('s2tw')
            converted = cc.convert(target)
            #print(converted)
            return converted
        else:
            DetectorFactory.seed = 0

            try:
                if detect(to_check) == "zh-cn":
                    cc = OpenCC('s2tw')
                    converted = cc.convert(target)
                    return converted
                else:
                    return target
            except langdetect.lang_detect_exception.LangDetectException:
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

def FileTranslator(file, update_to_same_file):
    file_data = ""
    count_line = 0
    total_line = GetFileLine(file)
    print('Translate %s ...'%file)
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            count_line += 1
            file_data += Convert(line)

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

def FileKeywordChecker(file):
    file_data = ""
    count_line = 0
    total_line = GetFileLine(file)
    print('Check %s ...'%file)
    with open(file, "r", encoding="utf-8") as f:
        file_data = file + ","
        for line in f:
            count_line += 1
            file_data += Checker(line)

            if total_line != 0:
                process = int((count_line / total_line) * 100)
                print("\r", end="")
                print("Process: {}%: ".format(process), "▓" * (process // 2), end="")
                sys.stdout.flush()
        file_data = file_data + "\n"

    record_file = "Keyword.csv"
            
    with open(record_file, "a", encoding="utf-8") as f:
        f.write(file_data)
    print("\r", end="")
    print('Update %s okay'%record_file)

def Checker(line):
    keyword = ""
    if not IsAscii(line):
        substring = line.split("\"\'")
        for partstring in substring:
            if not IsAscii(partstring):
                keyword += ConvertZhs(partstring)
    return keyword

def ConvertZhs(target):
    if isinstance(target, str):
        to_check = re.sub("[a-zA-Z0-9\n\./_<>:;(),\{\}\[\]]\s","",target)
        to_check = to_check.replace("\r","")
        to_check = to_check.replace("\n","")
        #print("check string = %s>"%to_check)

        langid.set_languages(['en','zh','ja'])
        if langid.classify(to_check)[0] == "zh":
            return to_check + ","
        else:
            DetectorFactory.seed = 0

            try:
                if detect(to_check) == "zh-cn":
                    return to_check + ","
                else:
                    return ""
            except langdetect.lang_detect_exception.LangDetectException:
                return ""
    else:
        return ""

def Convert(line):
    if not IsAscii(line):
        substring = line.split("\"")
        for partstring in substring:
            if not IsAscii(partstring):
                if not IsSpecialCommand(partstring):
                    if not IsEqualSpeciificCommand(partstring):
                        if not IsOptionCommand(partstring):
                            converstring = ConvertZhsToZht_langid(partstring)
                        else:
                            converstring = SubConvert(partstring)
                        
                        if partstring != converstring:
                            line = line.replace(partstring, converstring)
    return line

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
            if file.find(".json") != -1:
                FileTranslator(file, True)

def IsSpecialCommand(target):
    special = ["CallSemen", "CallCommon", "CallCutin", "CallStand", "TOES", "ParaAdd", "CommonEXP", "Callsem", "LocationFlag", "変身衣装", "LocationID", "TE:", "DE:", "ERS_MAKE_TEMPLATE_RANDOM"]
    for check in special:
        if target.find(check) != -1:
            return True
    return False

def IsEqualSpeciificCommand(target):
    Speciific = ["乱交", "乱交導入", "乱交中", "前戯", "前戯乱交", "内装", "近未来外観", "近未来内装", "○都市全景", "○学園内装", "〇下水道/近未来", "○体育館", "〇学園図書館", "〇学園外観", "病院内装", "学園", "廃工場", "住宅地", "皆川家", "銭湯", "市街地", "駅前", "総合病院", "繁華街", "下水道", "封鎖市街", "異界化学園地下", "侵蝕病棟", "崩壊暗域", "市民公園", "初痴漢", "触手怪人", "体重計", "通学生徒", "父との会話", "脱衣所", "街灯01", "街灯02", "偽物対策会議", "堕落", "種蒔・体育館", "催眠装置・体育", "催眠装置", "催眠体育", "黒服潜入1", "売春乱暴", "売春礼儀", "噴乳触手", "催眠装置・異界化", "催眠触手", "捕獲触手", "触手椅子", "捕獲触手2", "呪装1", "淫欲上限アップ", "GR対策会議", "GR対策会議2", "GR中枢司令部", "触手", "回避", "回避判定", "回避不能", "回避・無効", "回避率", "下着"]
    for check in Speciific:
        if target == check:
            return True
    return False    

def IsOptionCommand(target):
    if target.find("option:") != -1:
        return True
    else:
        return False

def SubConvert(target):
    substring = target.split("\n")
    for partstring in substring:
        converstring = ConvertZhsToZht_langid(partstring)
        if partstring != converstring:
            target = target.replace(partstring, converstring)
    return target

def ScriptTraversal(root_path):
    path = os.walk(root_path)
    for root, directories, files in path:
        #for directory in directories:
        #    print(directory)
        for file in files:
            if file.find(".js") != -1:
                FileKeywordChecker(file)

if __name__ == '__main__':
    FileTraversal(".")
    #ScriptTraversal(".")
    #(Convert("脚"))
 