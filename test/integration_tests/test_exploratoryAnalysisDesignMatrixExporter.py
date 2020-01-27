import os
import shutil
from unittest import TestCase

from source.data_model.dataset.RepertoireDataset import RepertoireDataset
from source.data_model.receptor.receptor_sequence.ReceptorSequence import ReceptorSequence
from source.data_model.receptor.receptor_sequence.SequenceMetadata import SequenceMetadata
from source.encodings.reference_encoding.ReferenceRepertoireEncoder import ReferenceRepertoireEncoder
from source.encodings.reference_encoding.SequenceMatchingSummaryType import SequenceMatchingSummaryType
from source.environment.EnvironmentSettings import EnvironmentSettings
from source.environment.LabelConfiguration import LabelConfiguration
from source.preprocessing.PatientRepertoireCollector import PatientRepertoireCollector
from source.reports.data_reports.SequenceLengthDistribution import SequenceLengthDistribution
from source.reports.encoding_reports.DesignMatrixExporter import DesignMatrixExporter
from source.reports.encoding_reports.MatchingSequenceDetails import MatchingSequenceDetails
from source.util.PathBuilder import PathBuilder
from source.util.RepertoireBuilder import RepertoireBuilder
from source.workflows.instructions.exploratory_analysis.ExploratoryAnalysisProcess import ExploratoryAnalysisInstruction
from source.workflows.instructions.exploratory_analysis.ExploratoryAnalysisUnit import ExploratoryAnalysisUnit


class TestExploratoryAnalysisDesignMatrixExporter(TestCase):

    def create_dataset(self, path):

        repertoires, metadata = RepertoireBuilder.build([["AAA"], ["AAAC"], ["ACA"], ["CAAA"], ["AAAC"], ["AAA"]], path,
                                            {"l1": [1, 1, 1, 0, 0, 0], "l2": [2, 3, 2, 3, 2, 3]})

        dataset = RepertoireDataset(repertoires=repertoires, params={"l1": [0, 1], "l2": [2, 3]}, metadata_file=metadata)
        return dataset

    def test_run(self):

        path = EnvironmentSettings.tmp_test_path + "explanalysisprocintegration/"
        PathBuilder.build(path)
        os.environ["cache_type"] = "test"

        dataset = self.create_dataset(path)

        label_config = LabelConfiguration()
        label_config.add_label("l1", [0, 1])
        label_config.add_label("l2", [2, 3])

        refs = [ReceptorSequence("AAAC", metadata=SequenceMetadata(v_gene="v1", j_gene="j1"))]

        preproc_sequence = [PatientRepertoireCollector()]

        units = {"named_analysis_1": ExploratoryAnalysisUnit(dataset=dataset, report=SequenceLengthDistribution(), batch_size=16),
                 "named_analysis_2": ExploratoryAnalysisUnit(dataset=dataset, report=SequenceLengthDistribution(), preprocessing_sequence=preproc_sequence),

                 "named_analysis_3": ExploratoryAnalysisUnit(dataset=dataset, report=MatchingSequenceDetails(max_edit_distance=1, reference_sequences=refs),
                                         label_config=label_config,
                                         encoder=ReferenceRepertoireEncoder(max_edit_distance=1,
                                                                            summary=SequenceMatchingSummaryType.COUNT,
                                                                            reference_sequences=refs)),
                 "named_analysis_4": ExploratoryAnalysisUnit(dataset=dataset,
                                                             report=DesignMatrixExporter(),
                                                             label_config=label_config,
                                                             encoder=ReferenceRepertoireEncoder(max_edit_distance=1,
                                                                                                summary=SequenceMatchingSummaryType.COUNT,
                                                                                                reference_sequences=refs))
                 }

        process = ExploratoryAnalysisInstruction(units)
        process.run(path + "results/")

        self.assertTrue(units["named_analysis_1"].batch_size == 16)
        self.assertTrue(os.path.isfile(path + "results/analysis_named_analysis_1/sequence_length_distribution.png"))
        self.assertTrue(os.path.isfile(path + "results/analysis_named_analysis_2/sequence_length_distribution.png"))
        self.assertTrue(os.path.isfile(path + "results/analysis_named_analysis_3/matching_sequence_overview.tsv"))

        shutil.rmtree(path)
