import os
from os.path import join

import rastervision as rv
from examples.utils import str_to_bool


class CowcObjectDetectionExperiments(rv.ExperimentSet):
    def exp_main(self, raw_uri, processed_uri, root_uri, test_run=False):
        """Object detection on COWC (Cars Overhead with Context) Potsdam dataset

        Args:
            raw_uri: (str) directory of raw data
            processed_uri: (str) directory of processed data
            root_uri: (str) root directory for experiment output
            test_run: (bool) if True, run a very small experiment as a test and generate
                debug output
        """
        test_run = str_to_bool(test_run)
        exp_id = 'cowc-object-detection'
        num_steps = 100000
        batch_size = 8
        debug = False
        train_scene_ids = ['2_10', '2_11', '2_12', '2_14', '3_11',
                           '3_13', '4_10', '5_10', '6_7', '6_9']
        val_scene_ids = ['2_13', '6_8', '3_10']

        if test_run:
            exp_id += '-test'
            num_steps = 1
            batch_size = 1
            debug = True
            train_scene_ids = train_scene_ids[0:1]
            val_scene_ids = val_scene_ids[0:1]

        task = rv.TaskConfig.builder(rv.OBJECT_DETECTION) \
                            .with_chip_size(300) \
                            .with_classes({'vehicle': (1, 'red')}) \
                            .with_chip_options(neg_ratio=1.0,
                                               ioa_thresh=0.8) \
                            .with_predict_options(merge_thresh=0.1,
                                                  score_thresh=0.5) \
                            .build()

        backend = rv.BackendConfig.builder(rv.TF_OBJECT_DETECTION) \
                                  .with_task(task) \
                                  .with_model_defaults(rv.SSD_MOBILENET_V1_COCO) \
                                  .with_debug(debug) \
                                  .with_batch_size(batch_size) \
                                  .with_num_steps(num_steps) \
                                  .build()

        def make_scene(id):
            img_uri = join(
                raw_uri, '4_Ortho_RGBIR/top_potsdam_{}_RGBIR.tif'.format(id))
            label_uri = join(
                processed_uri, 'labels', 'all', 'top_potsdam_{}_RGBIR.json'.format(id))

            return rv.SceneConfig.builder() \
                                 .with_id(id) \
                                 .with_task(task) \
                                 .with_raster_source(img_uri, channel_order=[0, 1, 2]) \
                                 .with_label_source(label_uri) \
                                 .build()

        train_scenes = [make_scene(id) for id in train_scene_ids]
        val_scenes = [make_scene(id) for id in val_scene_ids]

        dataset = rv.DatasetConfig.builder() \
                                  .with_train_scenes(train_scenes) \
                                  .with_validation_scenes(val_scenes) \
                                  .build()

        experiment = rv.ExperimentConfig.builder() \
                                        .with_id(exp_id) \
                                        .with_root_uri(root_uri) \
                                        .with_task(task) \
                                        .with_backend(backend) \
                                        .with_dataset(dataset) \
                                        .build()

        return experiment


if __name__ == '__main__':
    rv.main()
