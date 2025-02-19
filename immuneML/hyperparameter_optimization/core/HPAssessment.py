import datetime
from pathlib import Path
from typing import List

from immuneML.data_model.dataset.Dataset import Dataset
from immuneML.environment.Label import Label
from immuneML.environment.LabelConfiguration import LabelConfiguration
from immuneML.hyperparameter_optimization.HPSetting import HPSetting
from immuneML.hyperparameter_optimization.core.HPSelection import HPSelection
from immuneML.hyperparameter_optimization.core.HPUtil import HPUtil
from immuneML.hyperparameter_optimization.states.HPAssessmentState import HPAssessmentState
from immuneML.hyperparameter_optimization.states.TrainMLModelState import TrainMLModelState
from immuneML.ml_methods.MLMethod import MLMethod
from immuneML.reports.ReportUtil import ReportUtil
from immuneML.util.PathBuilder import PathBuilder
from immuneML.workflows.instructions.MLProcess import MLProcess
import ray


@ray.remote
class HPAssessment:

    @staticmethod
    def _combine_states(states: List[TrainMLModelState]) -> TrainMLModelState:
        combined_state = states[0]

        for state in states[1:]:
            combined_state.hp_settings.extend(state.hp_settings)
            combined_state.metrics.update(state.metrics)
            combined_state.context.update(state.context)
            combined_state.reports.update(state.reports)
            combined_state.optimal_hp_items.update(state.optimal_hp_items)
            combined_state.optimal_hp_item_paths.update(state.optimal_hp_item_paths)
            combined_state.assessment_states.extend(state.assessment_states)
            combined_state.report_results.extend(state.report_results)

        return combined_state

    @staticmethod
    def run_assessment(state: TrainMLModelState) -> TrainMLModelState:
        
        state = HPAssessment._create_root_path(state)
        train_val_datasets, test_datasets = HPUtil.split_data(state.dataset, state.assessment, state.path, state.label_configuration)
        n_splits = len(train_val_datasets)


        # for outer split parralell  
        if False:
            states = []

            ### split into n ray tasks
            for index in range(n_splits):
                states.append(HPAssessment.run_assessment_split.remote(state, train_val_datasets[index], test_datasets[index], 0, index))

            states = ray.get(states)

            ### combine every state into a single state (last state)
            combined_state = HPAssessment._combine_states(states)

            return combined_state
        else: 
            for index in range(n_splits):
                state = HPAssessment.run_assessment_split(state, train_val_datasets[index], test_datasets[index], index, n_splits)
            
            return state



    @staticmethod
    def _create_root_path(state: TrainMLModelState) -> TrainMLModelState:
        name = state.name if state.name is not None else "result"
        state.path = state.path / name
        return state

    @staticmethod
    def run_assessment_split(state, train_val_dataset, test_dataset, split_index: int, n_splits):
        """run inner CV loop (selection) and retrain on the full train_val_dataset after optimal model is chosen"""

        print(
            f'{datetime.datetime.now()}: Training ML model: running outer CV loop: started split {split_index + 1}/{n_splits}.\n',
            flush=True)

        current_path = HPAssessment.create_assessment_path(state, split_index)

        assessment_state = HPAssessmentState(split_index, train_val_dataset, test_dataset, current_path,
                                             state.label_configuration)

        state.assessment_states.append(assessment_state)

        state = HPSelection.run_selection(state, train_val_dataset, current_path, split_index)
        state = HPAssessment.run_assessment_split_per_label(state, split_index)


        assessment_state.train_val_data_reports = ReportUtil.run_data_reports(train_val_dataset, state.assessment.reports.data_split_reports.values(),
                                                                              current_path / "data_report_train", state.number_of_processes, state.context)
        assessment_state.test_data_reports = ReportUtil.run_data_reports(test_dataset, state.assessment.reports.data_split_reports.values(),
                                                                         current_path / "data_report_test", state.number_of_processes, state.context)

        print(
            f'{datetime.datetime.now()}: Training ML model: running outer CV loop: finished split {split_index + 1}/{n_splits}.\n',
            flush=True)

        return state

    @staticmethod
    def run_assessment_split_per_label(state: TrainMLModelState, split_index: int):
        """iterate through labels and hp_settings and retrain all models"""
        n_labels = state.label_configuration.get_label_count()

        for idx, label in enumerate(state.label_configuration.get_label_objects()):

            print(f"{datetime.datetime.now()}: Training ML model: running the inner loop of nested CV: "
                  f"retrain models for label {label.name} (label {idx + 1} / {n_labels}).\n", flush=True)

            path = state.assessment_states[split_index].path

            for index, hp_setting in enumerate(state.hp_settings):

                if hp_setting != state.assessment_states[split_index].label_states[label.name].optimal_hp_setting:
                    setting_path = path / f"{label.name}_{hp_setting}/"
                else:
                    setting_path = path / f"{label.name}_{hp_setting}_optimal/"

                train_val_dataset = state.assessment_states[split_index].train_val_dataset
                test_dataset = state.assessment_states[split_index].test_dataset
                state = HPAssessment.reeval_on_assessment_split(state, train_val_dataset, test_dataset, hp_setting,
                                                                setting_path, label, split_index)

            print(f"{datetime.datetime.now()}: Training ML model: running the inner loop of nested CV: completed retraining models "
                  f"for label {label.name} (label {idx + 1} / {n_labels}).\n", flush=True)

        return state

    @staticmethod
    def reeval_on_assessment_split(state, train_val_dataset: Dataset, test_dataset: Dataset, hp_setting: HPSetting, path: Path, label: Label,
                                   split_index: int) -> MLMethod:
        """retrain model for specific label, assessment split and hp_setting"""

        assessment_item = MLProcess(train_dataset=train_val_dataset, test_dataset=test_dataset, label=label,
                                    metrics=state.metrics,
                                    optimization_metric=state.optimization_metric, path=path, hp_setting=hp_setting,
                                    report_context=state.context,
                                    ml_reports=state.assessment.reports.model_reports.values(),
                                    number_of_processes=state.number_of_processes,
                                    encoding_reports=state.assessment.reports.encoding_reports.values(),
                                    label_config=LabelConfiguration([label])).run(split_index)

        state.assessment_states[split_index].label_states[label.name].assessment_items[str(hp_setting)] = assessment_item

        return state

    @staticmethod
    def create_assessment_path(state, split_index):
        current_path = state.path / f"split_{split_index + 1}"
        PathBuilder.build(current_path)
        return current_path
