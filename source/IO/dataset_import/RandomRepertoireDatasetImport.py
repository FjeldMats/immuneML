from source.IO.dataset_import.DataImport import DataImport
from source.data_model.dataset.RepertoireDataset import RepertoireDataset
from source.simulation.dataset_generation.RandomDatasetGenerator import RandomDatasetGenerator


class RandomRepertoireDatasetImport(DataImport):

    @staticmethod
    def import_dataset(params: dict, dataset_name: str) -> RepertoireDataset:
        """
        Returns randomly generated repertoire dataset according to the parameters;

        Specification:
            result_path: path/where/to/store/results/
            repertoire_count: 100 # number of random repertoires to generate
            sequence_count_probabilities:
                10: 0.5 # probability that any of the repertoires would have 10 receptor sequences
                20: 0.5
            sequence_length_probabilities:
                10: 0.5 # probability that any of the receptor sequences would be 10 amino acids in length
                12: 0.5
            labels:
                cmv:
                    True: 0.5 # probability of value True for label cmv to be assigned to any repertoire
                    False: 0.5
        """
        return RandomDatasetGenerator.generate_repertoire_dataset(repertoire_count=params["repertoire_count"],
                                                                  sequence_count_probabilities=params["sequence_count_probabilities"],
                                                                  sequence_length_probabilities=params["sequence_length_probabilities"],
                                                                  labels=params["labels"],
                                                                  path=params["result_path"])
