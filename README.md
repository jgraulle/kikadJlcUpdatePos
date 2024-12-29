Purpose
=======

Console tool to update kikad CPL POS file from a local cplEditJlc.csv file.
The CPL POS must be in "build" folder with the "-pos.csv" suffix.
The cplEditJlc.csv can update x and y position and rotation of each component in CPL POS file
with the following CSV column:
    - Package pattern: a regular expression in double quote to math the CPL POS "Package" column
    - PosX: a float to move x position of the mathing CPL POS
    - PosY: a float to move y position of the mathing CPL POS
    - Rot: a float to rotate orientation in degree of the mathing CPL POS

Setup
=====
For now is only compatible on Linux.

Run the setup.sh script to install in `~/.local/bin/`.
