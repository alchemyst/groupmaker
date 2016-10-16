Building groups avoiding minorities
===================================

It has been suggested that certain groups of people should not be in outnumbered in
teams [this document](http://info.catme.org/wp-content/uploads/Team-Maker_brochure_-_8_5x11_2013.pdf), for example, suggests that women should not be outnumbered). 

This project solves the problem of building such groups avoiding minorities as an MILP. It requires [PuLP](https://pypi.python.org/pypi/PuLP) for the modelling part.

To use the program simply build a CSV file or an Excel file containing student numbers in a column labeled "Nr" and other columns indicating minorities to be avoided, with a 1 in that column if that student is in that minority and a 0 if they aren't, for example:

| Nr | Language | Gender |
| -- | -------- | ------ |
| 1  |    0     |   0    |
| 2  |    0     |   0    |
| 3  |    1     |   0    |
| 4  |    1     |   0    |
| 5  |    0     |   1    |
| 6  |    1     |   1    |
| 7  |    0     |   0    |
| 8  |    0     |   1    |
| 9  |    1     |   1    |

Now, call `groupmaker.py` from the commandline with this file as the first arguent and the number of students per group as the second:

    python groupmaker.py miniclasslist.csv 3
    
You should see output like this:

    Trying <function _make_parser_function.<locals>.parser_f at 0x11085a510>
    9 students, 3 groups

There will be a new file called `output.csv` in the directory where you called the program from with the same data as the input file, but an extra column indicating the group number the student has been assigned to.


