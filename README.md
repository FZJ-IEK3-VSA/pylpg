<a href="https://www.fz-juelich.de/iek/iek-3/EN/Forschung/_Process-and-System-Analysis/_node.html"><img src="https://www.fz-juelich.de/SharedDocs/Bilder/IBG/IBG-3/DE/Plant-soil-atmosphere%20exchange%20processes/INPLAMINT%20(BONARES)/Bild3.jpg?__blob=poster" alt="Forschungszentrum Juelich Logo" width="230px"></a> 


# pyLPG

This package provides bindings to execute the LPG from python.

Basically it converts your settings into a JSON file for the LPG that
specifies what the LPG should calculate, starts the binary, 
waits for the results and then returns the results as pandas dataframe.

Look into the test_pylpg.py for examples on use.

Note that this package contains the full LPG binaries and the database.

If you want to use a different database than the one that comes with the package, you need to replace the files.


## License

MIT License

Copyright (C) 2016-2019 Leander Kotzur (FZJ IEK-3), Maximilian Hoffmann (FZJ IEK-3), Peter Markewitz (FZJ IEK-3), Martin Robinius (FZJ IEK-3), Detlef Stolten (FZJ IEK-3)

You should have received a copy of the MIT License along with this program.
If not, see https://opensource.org/licenses/MIT

## About Us 

<a href="http://www.fz-juelich.de/iek/iek-3/EN/Forschung/_Process-and-System-Analysis/_node.html"><img src="https://www.fz-juelich.de/SharedDocs/Bilder/IEK/IEK-3/Abteilungen2015/VSA_DepartmentPicture_2019-02-04_459x244_2480x1317.jpg?__blob=normal" width="400px" alt="Abteilung VSA"></a> 

We are the [Techno-Economic Energy Systems Analysis](https://www.fz-juelich.de/iek/iek-3/EN/Forschung/_Process-and-System-Analysis/_node.html) department at the [Institute of Energy and Climate Research: Electrochemical Process Engineering (IEK-3)](https://www.fz-juelich.de/iek/iek-3/EN/Home/home_node.html) belonging to the [Forschungszentrum Jülich](https://www.fz-juelich.de/). Our interdisciplinary department's research is focusing on energy-related process and systems analyses. Data searches and system simulations are used to determine energy and mass balances, as well as to evaluate performance, emissions and costs of energy systems. The results are used for performing comparative assessment studies between the various systems. Our current priorities include the development of energy strategies, in accordance with the German Federal Government’s greenhouse gas reduction targets, by designing new infrastructures for sustainable and secure energy supply chains and by conducting cost analysis studies for integrating new technologies into future energy market frameworks.
