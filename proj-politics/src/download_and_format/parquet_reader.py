##!/usr/bin/env python
"""
    An object that chunks a list of the partitions to read into larger groups and returns a chunksize similar to the pandas read
    csv function
"""

#imports
import pyarrow.parquet as pq
from pathlib import Path

__author__ = "Dylan Smith"
__copyright__ = "Copyright (C) 2020 Dylan Smith"
__credits__ = ["Dylan Smith"]

__license__ = "Personal Use"
__version__ = "1.0"
__maintainer__ = "Dylan Smith"
__email__ = "-"

class ParquetReader(object):
    """ 
    An object that splits up reading large partitioned parquet files to enable quicker scans.

    """
    def __init__(self, parquet_path, partition_nm, n = 40):
        """ Object that runs all the SQL commands in the projects
            ::param parquet_path: A Pathlib path where the parquet file is stored
            ::param n: The size of each group
        """
        dirs = [x for x in parquet_path.iterdir() if x.is_dir()]
        self.partition_nm = partition_nm
        self.parquet_path = parquet_path
        self.grouped_pars = [dirs[i * n:(i + 1) * n] for i in range((len(dirs) + n - 1) // n )]
        self.ix = 0
        self.max_ix = len(self.grouped_pars)

    def __iter__(self):
        """ Function that allows the object to be an iterator
        """
        return self

    def __next__(self):
        """ As the iterator goes through each object, get the next group of partitions and read into a pandas dataset
            returns: Returns a pandas dataset with the appropriate amount of objects
        """
        if self.ix < self.max_ix:
            filter_list = [[(self.partition_nm, '=', x.name.split("=")[1])] for x in self.grouped_pars[self.ix]]
            dataset = pq.ParquetDataset(self.parquet_path, filters=filter_list)
            self.ix += 1
            return dataset.read().to_pandas()

        raise StopIteration
