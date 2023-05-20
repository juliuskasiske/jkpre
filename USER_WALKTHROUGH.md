# User Walkthrough

Using jkpre is as simple as a few lines of code. For importing and applying some functionality, just follow the following steps.

## 1. Importing the module and instantiating the Redundancy object
Importing is done as follows
```Python
from jkpre.selection import Redundancy
red_analysis = Redundancy(input_data)
```

Note that the constructor of Redundancy does not require passed input data right away. It can alternatively be passed by setting the ``data`` attribute.

## 2. Splitting the data into categorical and continuous
```Python
# if data passed during instantiation
red_analysis.split_data()

# if data not passed during instantiation or by setting data attribute
red_analysis.split_data(input_data)
```

The method ``split_data`` will both return the two subtables, and save them in their respective instance attributes. The ``data`` attribute will not be mutated.

## 3. Creating correlation matrix for continuous variables
```Python
red_analysis.correlate_continuous()
```

Note that ``correlate_continuous`` will only return the ggplot object and not save it to any attribute.
