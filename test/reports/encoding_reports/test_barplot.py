import random
import shutil
import string
from unittest import TestCase

import numpy as np
import pandas as pd
from scipy import sparse

from source.data_model.dataset.RepertoireDataset import RepertoireDataset
from source.data_model.encoded_data.EncodedData import EncodedData
from source.environment.EnvironmentSettings import EnvironmentSettings
from source.reports.encoding_reports.barplot.Barplot import Barplot


class TestBarplot(TestCase):

    def test_generate(self):

        path = EnvironmentSettings.root_path + "test/tmp/barplot/"

        sequences = [''.join(random.choices(string.ascii_uppercase, k=12)) for i in range(3)]

        encoded_data = {
            'examples': sparse.csr_matrix(np.random.normal(50, 10, 200 * 3).reshape((200, 3))),
            'example_ids': [''.join(random.choices(string.ascii_uppercase, k=4)) for i in range(200)],
            'labels': {
                "patient": np.array([i for i in range(40) for _ in range(5)]),
                "week": np.array([0, 1, 2, 3, 4] * 40),
                "status": np.array(["R"] * 50 + ["NR"] * 50 + ["P"] * 50 + ["O"] * 50),
                "age": np.array([0] * 100 + [1] * 100),
                "gad": np.array([0] * 100 + [1] * 100),
                "znt8": np.array([1] * 100 + [0] * 100),
                "ia2": np.array([2] * 100 + [1] * 100)
            },
            'feature_names': sequences,
            'feature_annotations': pd.DataFrame({
                "sequence": sequences,
                "v_gene": [''.join(random.choices(string.ascii_uppercase, k=1)) for i in range(3)],
                "antigen": ["GAD"] * 2 + ["INSB"] * 1
            }),
            'encoding': "random"
        }

        dataset = RepertoireDataset(encoded_data=EncodedData(**encoded_data))

        report = Barplot(dataset=dataset,
                                      result_path=path,
                                      result_name="test",
                                      x="status",
                                      color="age",
                                      facet_columns=["week"],
                                      facet_rows=["feature"],
                                      height=6,
                                      palette={"NR": "yellow"})

        report.generate()

        shutil.rmtree(path)