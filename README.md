Building groups avoiding minorities
===================================

It has been suggested that certain groups of people should not be in outnumbered in
teams [this document](http://info.catme.org/wp-content/uploads/Team-Maker_brochure_-_8_5x11_2013.pdf), for example, suggests that women should not be outnumbered). 

This project solves the problem of building such groups avoiding minorities as an MILP. It requires [PuLP](https://pypi.python.org/pypi/PuLP) for the modelling part.

It can also ensure that students are equally divided with respect to groups.

To use the program, first build a CSV file or an Excel file containing one row for each student.
It should contain student numbers in a column labeled "Nr".
If a column should be used to avoid minorities, mark it with "nomin" at the end.
Place a 1 in that column if that student is in that minority and a 0 if they aren't.
If a column called "Grade" is found, it will be used to distribute students according to grade.
An example of a small class list is included:

| Nr | Language nomin | Gender nomin | Grade |
| -- | -------------- | ------------ | ----- |
| 1  |       0        |       0      |  46   |
| 2  |       0        |       0      |  46   |
| 3  |       1        |       0      |  58   |
| 4  |       1        |       0      |  31   |
| 5  |       0        |       1      |  57   |
| 6  |       1        |       1      |  80   |
| 7  |       0        |       0      |  67   |
| 8  |       0        |       1      |  47   |
| 9  |       1        |       1      |  80   |

| First Header  | Second Header |
| ------------- | ------------- |
| Content Cell  | Content Cell  |
| Content Cell  | Content Cell  |

Now, call `groupmaker.py` from the commandline with this file as the first arguent and the number of students per group as the second:

    python groupmaker.py miniclasslist.csv 3
    
You should see output like this:

    Trying <function _make_parser_function.<locals>.parser_f at 0x11085a510>
    9 students, 3 groups

There will be a new file called `output.csv` in the directory where you called the program from with the same data as the input file, but an extra column indicating the group number the student has been assigned to.

With the default settings, the grades will not be taken into account. 
To ensure distribution of grades, you need to specify the `--markgroupcount` option.
Grades are distrubuted by first calculating mark groups by dividing the class into ngroups + 1 quintiles.
`markgroupcount` specifies how many of each of these quintiles a group should have.
Start conservatively by specifying one of each group.
This may still not be feasible, so you can specify that the mark groups overlap by a certain percentage by specifying `--markoverlap`, which will allow the quintiles to overlap.

For example, if there are 3 people per group, the quintiles will be 0, 33, 66 and 100.
There are three mark groups - 0-33, 33-66 and 66-100.
With `markoverlap`=20 (which results in a feasible solution), the mark groups are expanded to 0-53, 13-86, 46-100.
