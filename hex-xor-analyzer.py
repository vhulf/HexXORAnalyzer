#!/usr/bin/python3

## DONE! :: FIX BINARY FILE READING! (--asText necessary for now!) [needed to add a .decode!]
## DONE! :: ADD SUPPORT FOR BRUTING.... how to integrate it?? [SINGLE COMMAND MODE ADDED!]
## TODO :: IMPLEMENT A BRUTE FORCING TO GET XOR KEY WHICH EXISTS IN A BIN??? MAYBE SINGLE COMMAND MODE WONT BE USED BY BASH SCRIPT NOW?

import string
from subprocess import call
import binascii
from os import name
 
def clear():
    # check and make call for specific operating system
    _ = call('clear' if name == 'posix' else 'cls')

def splitByXorLenThenHexorem(inputStr, xorHex):
    # get rid of any spaces or tabs
    inputStr = inputStr.translate(str.maketrans('', '', string.whitespace))
    outputStr = ""
    for _iter in range(0, int(len(inputStr)//len(xorHex))):
        if hexorem(inputStr[0:len(xorHex)], xorHex) == "NIL":
            break
        outputStr += hexorem(inputStr[0:len(xorHex)], xorHex)
        inputStr = inputStr[len(xorHex):]
    
    # print("endStateOfInput: " + inputStr)
    return str(outputStr)

def hexorem(a, b):
    if len(a) > len(b):
        a = a[0:len(b)]
    elif len(b) > len(a):
        b = b[0:len(a)]
    
    if "-" in a or "-" in b:
        result = "--"
    else:
        result = "~~"
        try:
            result = str('%x' % (int(a,16)^int(b,16)))
        except:
            print("XOR failure!")

    while len(result) < len(a):
        result = "0" + result

    return str(result)

def getStrFromInputFile(filePath, asText):
    outputStr = ""
    if asText:
        with open(filePath, 'r') as file:
            outputStr = file.read().replace('\n', '')
    else:
        with open(filePath, 'rb') as file:
            outputStr = binascii.hexlify(file.read()).decode("utf-8")
    
    return str(outputStr)

def outputHelp():
    print("------------------------------------------------------------------------------------------------------")
    print(".                                                                                                    .")
    print(".                                     ~~~ Auxiliary Commands ~~~                                     .")
    print(".                                                                                                    .")
    print(".  -> pairSize [NUM] ... EX: pairSize 2  , sets length of HEX pairs [AFFECTS ASCII, must be 2-4]     .")
    print(".  -> blockSize [NUM] ... EX: blockSize 16 , sets pairs per row [DOES NOT EFFECT COMPUTE]            .")
    print(".  -> ascii ... EX: ascii , enables or disables attempted ascii output ('._' = non-ascii char)       .")
    print(".  -> quit ... EX: quit , quits the analysis script (alias: 'exit')                                  .")
    print(".  -> help ... EX: help , displays this help dialog                                                  .")
    print(".                                                                                                    .")
    print(".  HEX input '00' can always be used to return to original input...                                  .")
    print("------------------------------------------------------------------------------------------------------")

def outputHeader():
    print("-----------------------------------------------------------------------")
    print(".                       XOR HEX Analysis Tool                         .")
    print(".                                                                     .")
    print(".      Please input the next XOR value to carry out...  (as hex)      .")
    print(".    or type 'help' for other possible commands and their usage...    .")
    print("-----------------------------------------------------------------------")

def outputMonitorView(stringForView, pairLength, blockLength, attemptAscii):
    print(" ")
    pairsSoFar = 0
    for _iter in range(0, len(stringForView)//pairLength):
        hexPair = stringForView[0:pairLength]
        if attemptAscii and "-" not in hexPair:
            # attempt to print out in ASCII mode, if it fails print out filler text "._"
            try:
                byteString = bytes.fromhex(hexPair)
                print(byteString.decode("ASCII"), end=" ", flush="True")
            except:
                print("._", end=" ", flush="True")
        else:
            print(hexPair, end=" ", flush="True")
        pairsSoFar += 1
        if pairsSoFar == blockLength:
            pairsSoFar = 0
            print(" ")
        
        stringForView = stringForView[pairLength:]
    
    print(" ")

### Command for usage by other scripts! Gunna be utilized to create some "find the key in its own binary" type bruteforcing...
def XORItAndReturn(fileString, xorKey, pairLen=2, asciiOut=True):
    workingString = splitByXorLenThenHexorem(fileString, xorKey)

    returnString = ""
    for _iter in range(0, len(workingString)//pairLen):
        hexPair = workingString[0:pairLen]
        if asciiOut and "-" not in hexPair:
            # attempt to print out in ASCII mode, if it fails print out filler text "._"
            try:
                byteString = bytes.fromhex(hexPair)
                print(byteString.decode("ASCII"), end=" ", flush="True")
            except:
                print("._", end=" ", flush="True")
        else:
            print(hexPair, end=" ", flush="True")
        
        workingString = workingString[pairLen:]
    

    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="A tool for analyzing binary data represented as HEX against different XOR key candidates, including attempted ASCII output")
    parser.add_argument("--file", "-f", required=True, help="binary data file... for files which have already been converted to text use --asText or -t")
    parser.add_argument("--pairLength", "-p", required=False, default=2, help="amount of characters to each hex pair in monitoring view (default: 2)")
    parser.add_argument("--blockLength", "-b", required=False, default=16, help="amount of pairs to be output per block in monitoring view (default: 16)")
    parser.add_argument("--asText", "-t", required=False,  default=False, action="store_true", help="for input files which have already been converted into text-based representation, space deliniated OK!")
    parser.add_argument("--noClear", "-n", required=False,  default=False, action="store_true", help="disables terminal clearing, allowing for earlier output to be reviewed via terminal history")
    parser.add_argument("--singleCommand", "-s", required=False,  default=False, help="enables 'just XOR it' mode, will issue a single xor input (or other command) and display output, useful for integration with other tooling (like bash scripts) for brute force searching! (usage: -s FF)")
    parser.add_argument("--asciiMode", "-a", required=False, default=False, action="store_true", help="enable ascii mode immediately")
    parser.add_argument("--textIn", "-i", required=False, default=False, action="store_true", help="changes the --file argument to a direct text input")
    args = parser.parse_args()

    quit = False

    if not args.textIn:
        fileString = getStrFromInputFile(args.file, args.asText)
    else:
        fileString = args.file

    command = "00 0"
    latestHexXor = "00"

    ## Begin input prompt loop!
    while not quit:
        if not args.singleCommand:
            if not args.noClear:
                clear()
            outputHeader()

        if args.singleCommand:
            command = args.singleCommand
        else:
            command, commandMod = command.split(" ")

        # match / case only introduced after version 3.10 :c
        if command == "pairSize":
            if commandMod:
                args.pairLength = int(commandMod)
                currentViewString = splitByXorLenThenHexorem(fileString, latestHexXor)
                outputMonitorView(currentViewString, args.pairLength, args.blockLength, args.asciiMode)
            else:
                print("Something went wrong, did you input a number in the expected format?")
        elif command == "blockSize":
            if commandMod:
                args.blockLength = int(commandMod)
                currentViewString = splitByXorLenThenHexorem(fileString, latestHexXor)
                outputMonitorView(currentViewString, args.pairLength, args.blockLength, args.asciiMode)
            else:
                print("Something went wrong, did you input a number in the expected format?")
        elif command == "ascii":
            args.asciiMode = False if args.asciiMode else True
            currentViewString = splitByXorLenThenHexorem(fileString, latestHexXor)
            outputMonitorView(currentViewString, args.pairLength, args.blockLength, args.asciiMode)
        elif command == "help":
            outputHelp()
        else:
            latestHexXor = command
            currentViewString = splitByXorLenThenHexorem(fileString, command)
            outputMonitorView(currentViewString, args.pairLength, args.blockLength, args.asciiMode)
        
        if command != "help" and not args.singleCommand:
            print("currentXOR: " + latestHexXor + ", ascii: " + str(args.asciiMode) + ", pairSize: " + str(args.pairLength) + ", blockSize: " + str(args.blockLength))
            print(" ")


        if args.singleCommand:
            command = "quit "
        else:
            command = input("-> ")

        if command == "":
            command = "00 0"
        elif command.find(" ") == -1:
            command += " "

        if command == "quit " or command == "exit ":
            quit = True
            break

        
       