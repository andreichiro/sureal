__copyright__ = "Copyright 2016-2018, Netflix, Inc."
__license__ = "Apache, Version 2.0"

import unittest
import six

import numpy as np

from sureal.config import SurealConfig
from sureal.tools.misc import import_python_file, indices
from sureal.dataset_reader import RawDatasetReader, SyntheticRawDatasetReader, \
    MissingDataRawDatasetReader, SelectSubjectRawDatasetReader, \
    CorruptSubjectRawDatasetReader, CorruptDataRawDatasetReader, PairedCompDatasetReader


class RawDatasetReaderTest(unittest.TestCase):

    def setUp(self):
        dataset_filepath = SurealConfig.test_resource_path('NFLX_dataset_public_raw.py')
        self.dataset = import_python_file(dataset_filepath)
        self.dataset_reader = RawDatasetReader(self.dataset)

    def test_read_dataset_stats(self):
        self.assertEqual(self.dataset_reader.num_ref_videos, 9)
        self.assertEqual(self.dataset_reader.max_content_id_of_ref_videos, 8)
        self.assertEqual(self.dataset_reader.num_dis_videos, 79)
        self.assertEqual(self.dataset_reader.num_observers, 26)

    def test_opinion_score_2darray(self):
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertAlmostEqual(np.mean(os_2darray), 3.544790652385589, places=4)
        self.assertAlmostEqual(np.mean(np.std(os_2darray, axis=1)), 0.64933186478291516, places=4)

    def test_dis_videos_content_ids(self):
        content_ids = self.dataset_reader.content_id_of_dis_videos
        self.assertAlmostEqual(np.mean(content_ids), 3.8607594936708862, places=4)

    def test_disvideo_is_refvideo(self):
        l = self.dataset_reader.disvideo_is_refvideo
        self.assertTrue(all(l[0:9]))

    def test_ref_score(self):
        self.assertEqual(self.dataset_reader.ref_score, 5.0)

    def test_to_persubject_dataset_wrong_dim(self):
        with self.assertRaises(AssertionError):
            dataset = self.dataset_reader.to_persubject_dataset(np.zeros(3000))
            self.assertEqual(len(dataset.dis_videos), 2054)

    def test_to_persubject_dataset(self):
        dataset = self.dataset_reader.to_persubject_dataset(np.zeros([79, 26]))
        self.assertEqual(len(dataset.dis_videos), 2054)


class RawDatasetReaderPartialTest(unittest.TestCase):

    def setUp(self):
        dataset_filepath = SurealConfig.test_resource_path('NFLX_dataset_public_raw_PARTIAL.py')
        self.dataset = import_python_file(dataset_filepath)
        self.dataset_reader = RawDatasetReader(self.dataset)

    def test_read_dataset_stats(self):
        self.assertEqual(self.dataset_reader.num_ref_videos, 7)
        self.assertEqual(self.dataset_reader.max_content_id_of_ref_videos, 8)
        self.assertEqual(self.dataset_reader.num_dis_videos, 51)
        self.assertEqual(self.dataset_reader.num_observers, 26)

    def test_opinion_score_2darray(self):
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertAlmostEqual(np.mean(os_2darray), 3.4871794871794872, places=4)
        self.assertAlmostEqual(np.mean(np.std(os_2darray, axis=1)), 0.65626252041788125, places=4)

    def test_dis_videos_content_ids(self):
        content_ids = self.dataset_reader.content_id_of_dis_videos
        self.assertAlmostEqual(np.mean(content_ids), 3.9215686274509802, places=4)

    def test_disvideo_is_refvideo(self):
        l = self.dataset_reader.disvideo_is_refvideo
        self.assertTrue(all(l[0:7]))

    def test_ref_score(self):
        self.assertEqual(self.dataset_reader.ref_score, 5.0)

    def test_to_persubject_dataset_wrong_dim(self):
        with self.assertRaises(AssertionError):
            dataset = self.dataset_reader.to_persubject_dataset(np.zeros(3000))
            self.assertEqual(len(dataset.dis_videos), 2054)

    def test_to_persubject_dataset(self):
        dataset = self.dataset_reader.to_persubject_dataset(np.zeros([79, 26]))
        self.assertEqual(len(dataset.dis_videos), 1326)


class SyntheticDatasetReaderTest(unittest.TestCase):

    def setUp(self):
        dataset_filepath = SurealConfig.test_resource_path('NFLX_dataset_public_raw.py')
        dataset = import_python_file(dataset_filepath)

        np.random.seed(0)
        info_dict = {
            'quality_scores': np.random.randint(1, 6, 79),
            'observer_bias': np.random.normal(0, 1, 26),
            'observer_inconsistency': np.abs(np.random.normal(0, 0.1, 26)),
            'content_bias': np.zeros(9),
            'content_ambiguity': np.zeros(9),
        }

        self.dataset_reader = SyntheticRawDatasetReader(dataset, input_dict=info_dict)

    def test_read_dataset_stats(self):
        self.assertEqual(self.dataset_reader.num_ref_videos, 9)
        self.assertEqual(self.dataset_reader.num_dis_videos, 79)
        self.assertEqual(self.dataset_reader.num_observers, 26)

    def test_opinion_score_2darray(self):
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertAlmostEqual(np.mean(os_2darray), 3.1912209428772669, places=4)

    def test_dis_videos_content_ids(self):
        content_ids = self.dataset_reader.content_id_of_dis_videos
        self.assertAlmostEqual(np.mean(content_ids), 3.8607594936708862, places=4)

    def test_disvideo_is_refvideo(self):
        l = self.dataset_reader.disvideo_is_refvideo
        self.assertTrue(all(l[0:9]))

    def test_ref_score(self):
        self.assertEqual(self.dataset_reader.ref_score, 5.0)

    def test_to_dataset(self):
        dataset = self.dataset_reader.to_dataset()

        old_scores = [dis_video['os'] for dis_video in self.dataset_reader.dataset.dis_videos]
        new_scores = [dis_video['os'] for dis_video in dataset.dis_videos]

        self.assertNotEqual(old_scores, new_scores)


class MissingDatasetReaderTest(unittest.TestCase):

    def setUp(self):
        dataset_filepath = SurealConfig.test_resource_path('NFLX_dataset_public_raw.py')
        dataset = import_python_file(dataset_filepath)

        np.random.seed(0)
        info_dict = {
            'missing_probability': 0.1,
        }

        self.dataset_reader = MissingDataRawDatasetReader(dataset, input_dict=info_dict)

    def test_opinion_score_2darray(self):
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertTrue(np.isnan(np.mean(os_2darray)))
        self.assertEqual(np.isnan(os_2darray).sum(), 201)

    def test_to_dataset(self):
        dataset = self.dataset_reader.to_dataset()

        old_scores = [dis_video['os'] for dis_video in self.dataset_reader.dataset.dis_videos]
        new_scores = [dis_video['os'] for dis_video in dataset.dis_videos]

        self.assertNotEqual(old_scores, new_scores)


class SelectedSubjectDatasetReaderTest(unittest.TestCase):

    def setUp(self):
        dataset_filepath = SurealConfig.test_resource_path('NFLX_dataset_public_raw.py')
        dataset = import_python_file(dataset_filepath)

        np.random.seed(0)
        info_dict = {
            'selected_subjects': range(5),
        }

        self.dataset_reader = SelectSubjectRawDatasetReader(dataset, input_dict=info_dict)

    def test_read_dataset_stats(self):
        self.assertEqual(self.dataset_reader.num_ref_videos, 9)
        self.assertEqual(self.dataset_reader.num_dis_videos, 79)
        self.assertEqual(self.dataset_reader.num_observers, 5)

    def test_opinion_score_2darray(self):
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertEqual(os_2darray.shape, (79, 5))

    def test_to_dataset(self):
        dataset = self.dataset_reader.to_dataset()

        old_scores = [dis_video['os'] for dis_video in self.dataset_reader.dataset.dis_videos]
        new_scores = [dis_video['os'] for dis_video in dataset.dis_videos]

        self.assertNotEqual(old_scores, new_scores)


class CorruptSubjectDatasetReaderTestWithCorruptionProb(unittest.TestCase):

    def setUp(self):
        dataset_filepath = SurealConfig.test_resource_path('NFLX_dataset_public_raw.py')
        self.dataset = import_python_file(dataset_filepath)

        np.random.seed(0)

    def test_opinion_score_2darray_with_corruption_prob(self):
        info_dict = {
            'selected_subjects': range(5),
            'corrupt_probability': 0.0,
        }
        self.dataset_reader = CorruptSubjectRawDatasetReader(self.dataset, input_dict=info_dict)
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertEqual(os_2darray.shape, (79, 26))
        self.assertAlmostEqual(np.mean(np.std(os_2darray, axis=1)), 0.64933186478291516, places=4)

    def test_opinion_score_2darray_with_corruption_prob2(self):
        info_dict = {
            'selected_subjects': range(5),
            'corrupt_probability': 0.2,
        }
        self.dataset_reader = CorruptSubjectRawDatasetReader(self.dataset, input_dict=info_dict)
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertEqual(os_2darray.shape, (79, 26))
        self.assertAlmostEqual(np.mean(np.std(os_2darray, axis=1)), 0.73123067709849221, places=4)

    def test_opinion_score_2darray_with_corruption_prob3(self):
        info_dict = {
            'selected_subjects': range(5),
            'corrupt_probability': 0.7,
        }
        self.dataset_reader = CorruptSubjectRawDatasetReader(self.dataset, input_dict=info_dict)
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertEqual(os_2darray.shape, (79, 26))
        self.assertAlmostEqual(np.mean(np.std(os_2darray, axis=1)), 0.85118397722242856, places=4)

    def test_opinion_score_2darray_with_corruption_prob4(self):
        info_dict = {
            'selected_subjects': range(5),
            'corrupt_probability': 1.0,
        }
        self.dataset_reader = CorruptSubjectRawDatasetReader(self.dataset, input_dict=info_dict)
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertEqual(os_2darray.shape, (79, 26))
        self.assertAlmostEqual(np.mean(np.std(os_2darray, axis=1)), 0.96532565883975119, places=4)


class CorruptSubjectDatasetReaderTest(unittest.TestCase):

    def setUp(self):
        dataset_filepath = SurealConfig.test_resource_path('NFLX_dataset_public_raw.py')
        dataset = import_python_file(dataset_filepath)

        np.random.seed(0)
        info_dict = {
            'selected_subjects': range(5),
        }

        self.dataset_reader = CorruptSubjectRawDatasetReader(dataset, input_dict=info_dict)

    def test_read_dataset_stats(self):
        self.assertEqual(self.dataset_reader.num_ref_videos, 9)
        self.assertEqual(self.dataset_reader.num_dis_videos, 79)
        self.assertEqual(self.dataset_reader.num_observers, 26)

    def test_opinion_score_2darray(self):
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertEqual(os_2darray.shape, (79, 26))
        self.assertAlmostEqual(np.mean(np.std(os_2darray, axis=1)), 0.93177573807000225, places=4)

    def test_to_dataset(self):
        dataset = self.dataset_reader.to_dataset()

        old_scores = [dis_video['os'] for dis_video in self.dataset_reader.dataset.dis_videos]
        new_scores = [dis_video['os'] for dis_video in dataset.dis_videos]

        self.assertNotEqual(old_scores, new_scores)


class CorruptDataDatasetReaderTest(unittest.TestCase):

    def setUp(self):
        dataset_filepath = SurealConfig.test_resource_path('NFLX_dataset_public_raw.py')
        dataset = import_python_file(dataset_filepath)

        np.random.seed(0)
        info_dict = {
            'corrupt_probability': 0.1,
        }

        self.dataset_reader = CorruptDataRawDatasetReader(dataset, input_dict=info_dict)

    def test_opinion_score_2darray(self):
        os_2darray = self.dataset_reader.opinion_score_2darray
        self.assertAlmostEqual(np.mean(np.std(os_2darray, axis=1)), 0.79796204942957094, places=4)

    def test_to_dataset(self):
        dataset = self.dataset_reader.to_dataset()

        old_scores = [dis_video['os'] for dis_video in self.dataset_reader.dataset.dis_videos]
        new_scores = [dis_video['os'] for dis_video in dataset.dis_videos]

        self.assertNotEqual(old_scores, new_scores)


class RawDatasetReaderPCTest(unittest.TestCase):

    def setUp(self):
        dataset_filepath = SurealConfig.test_resource_path('NFLX_dataset_public_raw.py')
        dataset = import_python_file(dataset_filepath)
        self.dataset_reader = RawDatasetReader(dataset)

    def test_dataset_to_pc_dataset(self):
        pc_dataset = self.dataset_reader.to_pc_dataset()
        pc_dataset_reader = PairedCompDatasetReader(pc_dataset)
        opinion_score_3darray = pc_dataset_reader.opinion_score_3darray
        self.assertEqual(np.nansum(opinion_score_3darray), 8242)
        self.assertEqual(np.nanmean(opinion_score_3darray), 0.816039603960396)
        self.assertEqual(np.nanmin(opinion_score_3darray), 0.5)
        self.assertEqual(np.nanmax(opinion_score_3darray), 1.0)

    def test_dataset_to_pc_dataset_within_subject(self):
        pc_dataset = self.dataset_reader.to_pc_dataset(pc_type='within_subject')
        pc_dataset_reader = PairedCompDatasetReader(pc_dataset)
        opinion_score_3darray = pc_dataset_reader.opinion_score_3darray
        self.assertEqual(np.nansum(opinion_score_3darray), 80106)
        self.assertEqual(np.nanmean(opinion_score_3darray), 0.8050935185278244)
        self.assertEqual(np.nanmin(opinion_score_3darray), 0.5)
        self.assertEqual(np.nanmax(opinion_score_3darray), 1.0)

    def test_dataset_to_pc_dataset_coin_toss(self):
        pc_dataset = self.dataset_reader.to_pc_dataset(tiebreak_method='coin_toss')
        pc_dataset_reader = PairedCompDatasetReader(pc_dataset)
        opinion_score_3darray = pc_dataset_reader.opinion_score_3darray
        self.assertEqual(np.nansum(opinion_score_3darray), 8242)
        self.assertEqual(np.nanmean(opinion_score_3darray), 1.0)
        self.assertEqual(np.nanmin(opinion_score_3darray), 1.0)
        self.assertEqual(np.nanmax(opinion_score_3darray), 1.0)

    def test_dataset_to_pc_dataset_random(self):
        import random
        random.seed(0)
        pc_dataset = self.dataset_reader.to_pc_dataset(randomness_level=0.5)
        pc_dataset_reader = PairedCompDatasetReader(pc_dataset)
        opinion_score_3darray = pc_dataset_reader.opinion_score_3darray
        self.assertEqual(np.nansum(opinion_score_3darray), 8242)
        # check: python2 values seem to fluctuate quite a bit
        self.assertAlmostEqual(np.nanmean(opinion_score_3darray), 0.85, delta=0.1)
        self.assertEqual(np.nanmin(opinion_score_3darray), 0.5)
        self.assertEqual(np.nanmax(opinion_score_3darray), 1.0)

    def test_dataset_to_pc_dataset_sampling_rate(self):
        import random
        random.seed(0)
        pc_dataset = self.dataset_reader.to_pc_dataset(sampling_rate=0.1)
        pc_dataset_reader = PairedCompDatasetReader(pc_dataset)
        opinion_score_3darray = pc_dataset_reader.opinion_score_3darray
        self.assertEqual(np.nansum(opinion_score_3darray), 844)
        self.assertAlmostEqual(np.nanmean(opinion_score_3darray), 0.85, delta=0.1)
        self.assertEqual(np.nanmin(opinion_score_3darray), 0.5)
        self.assertEqual(np.nanmax(opinion_score_3darray), 1.0)

    def test_dataset_to_pc_dataset_per_asset_sampling_rates(self):
        import random
        random.seed(0)
        pc_dataset = self.dataset_reader.to_pc_dataset(per_asset_sampling_rates=np.hstack([np.ones(39), np.ones(40) * 0.1]))
        pc_dataset_reader = PairedCompDatasetReader(pc_dataset)
        opinion_score_3darray = pc_dataset_reader.opinion_score_3darray
        self.assertEqual(np.nansum(opinion_score_3darray), 4550)
        self.assertAlmostEqual(np.nanmean(opinion_score_3darray), 0.85, delta=0.1)
        self.assertEqual(np.nanmin(opinion_score_3darray), 0.5)
        self.assertEqual(np.nanmax(opinion_score_3darray), 1.0)


if __name__ == '__main__':
    unittest.main()
