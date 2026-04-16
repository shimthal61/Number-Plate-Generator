# Number Plate Generator

## Task

A Number Plate is structure as:

![alt text](image.png)

Your task is to create a program that will generate a new number plate given:
- Memory Tag (e.g. YA)
- Date in the format dd/mm/yyyy (e.g. 01/01/2002)

## Rules

- The number plate must be unique and your program should not generate repeated number plates.
- The letters ‘Iʼ, ‘Qʼ and ‘Zʼ should not appear on your number plates as they are restricted as they look
too similar to other letters or numbers.

The age identifier is calculated from the last two numbers of the year in which the car was made. For
vehicles the year runs from March -> February. Furthermore, if the car was manufactured in the second half
of the year (September - February) then 50 must be added to the age identifier. e.g.

- March 2002 – Aug 2002 -> 02
- Sept 2002 – Feb 2003 -> 52

## Examples

Example 1
- Input: MV, 03/04/2010
- Ouput: MV10 FRH

Example 2
- Input: YA, 25/09/2001
- Output: YA51 YH