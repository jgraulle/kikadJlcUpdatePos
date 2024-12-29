#!/bin/python3

import os
import dataclasses
import re
import copy


BUILD_FOLDER_NAME = "./build"
POS_FILE_IN_SUFFIX = "-pos.csv"
POS_FILE_OUT_SUFFIX = "-pos-jlc.csv"
POS_FILE_HEADER_BEFORE = "Ref,Val,Package,PosX,PosY,Rot,Side"
POS_FILE_HEADER_AFTER = "Designator,Val,Package,Mid X,Mid Y,Rotation,Layer"
CPL_EDIT_FILE_PATH = "./cplEditJlc.csv"
CPL_EDIT_FILE_HEADER = "Package pattern,PosX,PosY,Rot"


def csvItemToStr(item: str) -> str:
    return item.strip().removeprefix('"').removesuffix('"').strip()


@dataclasses.dataclass
class CplEditItem():
    packageRegEx: re.Pattern
    posX: float
    posY: float
    rotDeg: float

    def __init__(self, csvLine: str, csvPath: str, csvLineNumber: int):
        columnExpected = CPL_EDIT_FILE_HEADER.count(",")+1
        assert columnExpected == 4
        strList = csvLine.strip().split(",")
        if len(strList) != columnExpected:
            raise ValueError(f"The file {csvPath} do not contains {columnExpected} at "
                             f"line {csvLineNumber}")
        self.packageRegEx = re.compile(csvItemToStr(strList[0]))
        self.posX = float(csvItemToStr(strList[1]))
        self.posY = float(csvItemToStr(strList[2]))
        self.rotDeg = float(csvItemToStr(strList[3]))


@dataclasses.dataclass
class PosItem():
    ref: str
    val: str
    package: str
    posX: float
    posY: float
    rotDeg: float
    side: str

    def __init__(self, csvLine: str, csvPath: str, csvLineNumber: int):
        columnExpected = POS_FILE_HEADER_BEFORE.count(",")+1
        assert columnExpected == 7
        strList = csvLine.strip().split(",")
        if len(strList) != columnExpected:
            raise ValueError(f"The file {csvPath} do not contains {columnExpected} at "
                             f"line {csvLineNumber}")
        self.ref = csvItemToStr(strList[0])
        self.val = csvItemToStr(strList[1])
        self.package = csvItemToStr(strList[2])
        self.posX = float(csvItemToStr(strList[3]))
        self.posY = float(csvItemToStr(strList[4]))
        self.rotDeg = float(csvItemToStr(strList[5]))
        self.side = csvItemToStr(strList[6])

    def toCsvLine(self) -> str:
        return f'"{self.ref}","{self.val}","{self.package}",{self.posX:.6f},{self.posY:.6f},' \
            f'{self.rotDeg:.6f},{self.side}\n'


def openCplEditFile(cplEditPath) -> list[CplEditItem]:
    cplEditList: list[CplEditItem] = []
    # Open CPL edit path
    with open(cplEditPath, "r", encoding="utf-8") as posFileIn:
        # For each line of edit file
        lineNumber = 0
        for lineStr in posFileIn:
            lineNumber += 1
            # If this line is the header
            if lineNumber == 1:
                # If this line is not the expected header
                lineStr = lineStr.strip()
                if lineStr != CPL_EDIT_FILE_HEADER:
                    # Raise error
                    raise ValueError(f"The file {cplEditPath} expected first line "
                                     f'"{CPL_EDIT_FILE_HEADER}" instead of "{lineStr}"')
            # If this line is not the header
            else:
                cplEditList.append(CplEditItem(lineStr, cplEditPath, lineNumber))
    return cplEditList


def processPosFile(fileInPath: str, cplEditList: list[CplEditItem]):
    # Open input file
    print(f'Process file "{fileInPath}"...')
    fileOutStr = ""
    with open(fileInPath, "r", encoding="utf-8") as fileIn:
        # For each line of input file
        lineNumberIn = 0
        for lineInStr in fileIn:
            lineNumberIn += 1
            # If this line is the header
            if lineNumberIn == 1:
                # If this line is not the expected header
                lineInStr = lineInStr.strip()
                if lineInStr != POS_FILE_HEADER_BEFORE:
                    # Raise error
                    raise ValueError(f"The file {fileInPath} do not expected first line "
                                     f"{POS_FILE_HEADER_BEFORE}")
                # Replace this line
                fileOutStr += POS_FILE_HEADER_AFTER + "\n"
            # If this line is not the header
            else:
                lineOutStr = ""
                # Split data
                posItemIn = PosItem(lineInStr, fileInPath, lineNumberIn)
                # For each CPL edit
                for cplEdit in cplEditList:
                    # If current line math current pattern
                    if cplEdit.packageRegEx.search(posItemIn.package):
                        # Generate line out
                        posItemOut = copy.deepcopy(posItemIn)
                        posItemOut.posX += cplEdit.posX
                        posItemOut.posY += cplEdit.posY
                        posItemOut.rotDeg = (posItemIn.rotDeg + cplEdit.rotDeg) % 360
                        if posItemOut.rotDeg > 180:
                            posItemOut.rotDeg -= 360
                        print(f'Pattern "{cplEdit.packageRegEx.pattern}" in "{fileInPath}" at '
                              f'line {lineNumberIn} update:')
                        if posItemIn.posX != posItemOut.posX:
                            print(f"\t- PosX from {posItemIn.posX} to {posItemOut.posX}")
                        if posItemIn.posY != posItemOut.posY:
                            print(f"\t- PosY from {posItemIn.posY} to {posItemOut.posY}")
                        if posItemIn.rotDeg != posItemOut.rotDeg:
                            print(f"\t- Rot from {posItemIn.rotDeg} to {posItemOut.rotDeg}")
                        lineOutStr = posItemOut.toCsvLine()
                        break
                # If line out not generated
                if lineOutStr == "":
                    # Copy it from line in
                    lineOutStr = lineInStr
                # Append this line
                fileOutStr += lineOutStr
    # Generate ouput file name
    posFileOutPath = fileInPath.removesuffix(POS_FILE_IN_SUFFIX) + POS_FILE_OUT_SUFFIX
    with open(posFileOutPath, "w", encoding="utf-8") as posFileOut:
        posFileOut.write(fileOutStr)


def main():
    # Open CPL edit file
    cplEditList = openCplEditFile(CPL_EDIT_FILE_PATH)
    # Process each file suffix by pos file suffix in build folder
    for fileName in os.listdir(BUILD_FOLDER_NAME):
        if fileName.endswith(POS_FILE_IN_SUFFIX):
            processPosFile(os.path.join(BUILD_FOLDER_NAME, fileName), cplEditList)


main()
