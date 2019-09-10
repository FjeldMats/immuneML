import pickle
import shutil
from unittest import TestCase

import pandas as pd

from source.data_model.dataset.RepertoireDataset import RepertoireDataset
from source.data_model.receptor.receptor_sequence.ReceptorSequence import ReceptorSequence
from source.data_model.receptor.receptor_sequence.SequenceMetadata import SequenceMetadata
from source.data_model.repertoire.SequenceRepertoire import SequenceRepertoire
from source.environment.EnvironmentSettings import EnvironmentSettings
from source.preprocessing.filters.DatasetChainFilter import DatasetChainFilter
from source.util.PathBuilder import PathBuilder


class TestDatasetChainFilter(TestCase):
    def test_process(self):
        rep1 = SequenceRepertoire(sequences=[ReceptorSequence("AAA", metadata=SequenceMetadata(chain="A"))])
        rep2 = SequenceRepertoire(sequences=[ReceptorSequence("AAC", metadata=SequenceMetadata(chain="B"))])

        path = EnvironmentSettings.root_path + "test/tmp/datasetchainfilter/"
        PathBuilder.build(path)
        with open(path + "rep1.pkl", "wb") as file:
            pickle.dump(rep1, file)
        with open(path + "rep2.pkl", "wb") as file:
            pickle.dump(rep2, file)

        metadata = pd.DataFrame({"CD": [1, 0]})
        metadata.to_csv(path + "metadata.csv")

        dataset = RepertoireDataset(filenames=[path + "rep1.pkl", path + "rep2.pkl"], metadata_file=path + "metadata.csv")

        dataset2 = DatasetChainFilter.process(dataset, {"keep_chain": "A", "result_path": path + "results/"})

        self.assertEqual(1, len(dataset2.get_filenames()))
        self.assertEqual(2, len(dataset.get_filenames()))

        metadata_dict = dataset2.get_metadata(["CD"])
        self.assertEqual(1, len(metadata_dict["CD"]))
        self.assertEqual(1, metadata_dict["CD"][0])

        for rep in dataset2.get_data():
            self.assertEqual("AAA", rep.sequences[0].get_sequence())

        shutil.rmtree(path)
