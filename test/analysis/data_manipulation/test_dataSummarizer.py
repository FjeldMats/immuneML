from unittest import TestCase

import numpy as np
from scipy import sparse
import pandas as pd

from source.data_model.dataset.Dataset import Dataset
from source.data_model.encoded_data.EncodedData import EncodedData
from source.analysis.data_manipulation.DataSummarizer import DataSummarizer
from source.analysis.criteria_matches.BooleanType import BooleanType
from source.analysis.criteria_matches.OperationType import OperationType
from source.analysis.criteria_matches.DataType import DataType


class TestDataSummarizer(TestCase):

    # 5 features, 3 repertoires. Each repertoire has 3 labels. Each feature has 2 annotations.

    encoded_data_1 = {
        'repertoires': sparse.csr_matrix(np.array([
            [1, 2, 3, 4, 5],
            [0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0]
        ])),
        'repertoire_ids': ['rep1', 'rep2', 'rep3'],
        'labels': {
            "diabetes": ['diabetes pos', 'diabetes neg', 'diabetes neg'],
            "celiac": ['celiac pos', 'celiac pos', 'celiac pos'],
            "cmv": ['cmv pos', 'cmv neg', 'cmv pos']
        },
        'feature_names': ['a', 'b', 'c', 'd', 'e'],
        'feature_annotations': pd.DataFrame({
            "specificity": ["cmv", "ebv", "cmv", "gluten", "gluten"],
            "p_val": [0.01, 0.00001, 0.1, 0, 0.0000001]
        })
    }

    dataset_1 = Dataset(encoded_data=EncodedData(**encoded_data_1),
                        filenames=[filename + ".tsv" for filename in encoded_data_1["repertoire_ids"]])

    encoded_data_2 = {
        'repertoires': sparse.csr_matrix(np.array([
            [1, 2, 3, 4, 5],
            [0, 0, 0, 1, 1],
            [1, 1, 0, 0, 0],
            [90, 10, 1, 3, 4],
            [0, 1, 1, 100, 200]
        ])),
        'repertoire_ids': ['rep1', 'rep2', 'rep3', 'rep4', 'rep5'],
        'labels': {
            "diabetes": ['diabetes pos', 'diabetes neg', 'diabetes neg', 'diabetes pos', 'diabetes pos'],
            "celiac": ['celiac pos', 'celiac pos', 'celiac pos', 'celiac neg', 'celiac pos'],
            "cmv": ['cmv pos', 'cmv neg', 'cmv pos', 'cmv pos', 'cmv neg']
         },
        'feature_names': ['a', 'b', 'c', 'd', 'e'],
        'feature_annotations': pd.DataFrame({
            "specificity": ["cmv", "ebv", "cmv", "gluten", "gluten"],
            "something": ["a", "b", "b", "a", "a"],
            "p_val": [0.01, 0.00001, 0.1, 0, 0.0000001]
        })
    }

    dataset_2 = Dataset(encoded_data=EncodedData(**encoded_data_2),
                        filenames=[filename + ".tsv" for filename in encoded_data_2["repertoire_ids"]])


    def test_filter_repertoires(self):

        dataset = TestDataSummarizer.dataset_1

        criteria = {
            "type": BooleanType.AND,
            "operands": [
                {
                    "type": OperationType.IN,
                    "allowed_values": ["celiac pos"],
                    "value": {
                        "type": DataType.COLUMN,
                        "name": "celiac"
                    }
                },
                {
                    "type": OperationType.IN,
                    "allowed_values": ["cmv pos"],
                    "value": {
                        "type": DataType.COLUMN,
                        "name": "cmv"
                    }
                }
            ]
        }

        filtered = DataSummarizer.filter_repertoires(dataset, criteria)

        self.assertTrue(filtered.get_repertoire_count() == 2)
        self.assertTrue(filtered.encoded_data.repertoires.shape[0] == 2)
        self.assertTrue(filtered.encoded_data.repertoires.shape[1] == 5)

    def test_filter_features(self):

        dataset = TestDataSummarizer.dataset_1

        criteria = {
            "type": BooleanType.OR,
            "operands": [
                {
                    "type": OperationType.IN,
                    "allowed_values": ["gluten"],
                    "value": {
                        "type": DataType.COLUMN,
                        "name": "specificity"
                    }
                },
                {
                    "type": OperationType.LESS_THAN,
                    "threshold": 0.0001,
                    "value": {
                        "type": DataType.COLUMN,
                        "name": "p_val"
                    }
                }
            ]
        }

        filtered = DataSummarizer.filter_features(dataset, criteria)

        self.assertTrue(filtered.get_repertoire_count() == 3)
        self.assertTrue(filtered.encoded_data.repertoires.shape[0] == 3)
        self.assertTrue(filtered.encoded_data.repertoires.shape[1] == 3)

    def test_annotate_repertoires(self):

        dataset = TestDataSummarizer.dataset_1

        criteria = {
            "type": BooleanType.AND,
            "operands": [
                {
                    "type": OperationType.IN,
                    "allowed_values": ["celiac pos"],
                    "value": {
                        "type": DataType.COLUMN,
                        "name": "celiac"
                    }
                },
                {
                    "type": OperationType.IN,
                    "allowed_values": ["cmv pos"],
                    "value": {
                        "type": DataType.COLUMN,
                        "name": "cmv"
                    }
                }
            ]
        }

        annotated = DataSummarizer.annotate_repertoires(dataset, criteria, "annotate")

        self.assertTrue(annotated.get_repertoire_count() == 3)
        self.assertTrue(annotated.encoded_data.repertoires.shape[0] == 3)
        self.assertTrue(annotated.encoded_data.repertoires.shape[1] == 5)

    def test_annotate_features(self):

        dataset = TestDataSummarizer.dataset_1

        criteria = {
            "type": BooleanType.OR,
            "operands": [
                {
                    "type": OperationType.IN,
                    "allowed_values": ["gluten"],
                    "value": {
                        "type": DataType.COLUMN,
                        "name": "specificity"
                    }
                },
                {
                    "type": OperationType.LESS_THAN,
                    "threshold": 0.0001,
                    "value": {
                        "type": DataType.COLUMN,
                        "name": "p_val"
                    }
                }
            ]
        }

        annotated = DataSummarizer.annotate_features(dataset, criteria, "annotate")

        self.assertTrue(annotated.get_repertoire_count() == 3)
        self.assertTrue(annotated.encoded_data.repertoires.shape[0] == 3)
        self.assertTrue(annotated.encoded_data.repertoires.shape[1] == 5)

    def test_annotate_features_2(self):

        dataset = TestDataSummarizer.dataset_1

        criteria = [
            {
                "column": "specificity",
                "type": "in",
                "value": ["gluten"]
            },
        ]

        criteria = {
            "type": OperationType.IN,
            "allowed_values": ["gluten"],
            "value": {
                "type": DataType.COLUMN,
                "name": "specificity"
            }
        }

        annotated = DataSummarizer.annotate_features(dataset, criteria, "annotate")

        self.assertTrue(annotated.get_repertoire_count() == 3)
        self.assertTrue(annotated.encoded_data.repertoires.shape[0] == 3)
        self.assertTrue(annotated.encoded_data.repertoires.shape[1] == 5)
