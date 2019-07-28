import os
import time
import unittest
import sys
import logging
import numpy as np
import yaml

import set_env
from ppdet.data.reader import Reader


class TestReader(unittest.TestCase):
    """Test cases for dataset.reader
    """

    @classmethod
    def setUpClass(cls):
        """ setup
        """
        prefix = os.path.dirname(os.path.abspath(__file__))
        coco_yml = os.path.join(prefix, 'coco.yml')
        with open(coco_yml, 'rb') as f:
            cls.coco_conf = yaml.load(f.read())

        cls.coco_conf['DATA']['TRAIN'] = set_env.coco_data['TRAIN']
        cls.coco_conf['DATA']['VAL'] = set_env.coco_data['VAL']

        rcnn_yml = os.path.join(prefix, 'rcnn_dataset.yml')

        with open(rcnn_yml, 'rb') as f:
            cls.rcnn_conf = yaml.load(f.read())

        cls.rcnn_conf['DATA']['TRAIN'] = set_env.coco_data['TRAIN']
        cls.rcnn_conf['DATA']['VAL'] = set_env.coco_data['VAL']

    @classmethod
    def tearDownClass(cls):
        """ tearDownClass """
        pass

    def test_train(self):
        """ Test reader for training
        """
        coco = Reader(
            self.coco_conf['DATA'], self.coco_conf['TRANSFORM'], maxiter=1000)
        train_rd = coco.train()
        self.assertTrue(train_rd is not None)

        ct = 0
        total = 0
        bytes = 0
        prev_ts = None
        for sample in train_rd():
            if prev_ts is None:
                start_ts = time.time()
                prev_ts = start_ts

            ct += 1
            bytes += 4 * sample[0][0].size * len(sample[0])
            self.assertTrue(sample is not None)
            cost = time.time() - prev_ts
            if cost >= 1.0:
                total += ct
                qps = total / (time.time() - start_ts)
                bps = bytes / (time.time() - start_ts)

                logging.info('got %d/%d samples in %.3fsec with qps:%d bps:%d' %
                             (ct, total, cost, qps, bps))
                bytes = 0
                ct = 0
                prev_ts = time.time()

        total += ct
        self.assertEqual(total, coco._maxiter)

    def test_val(self):
        """ Test reader for validation
        """
        coco = Reader(self.coco_conf['DATA'], self.coco_conf['TRANSFORM'], 10)
        val_rd = coco.val()
        self.assertTrue(val_rd is not None)

        # test 3 epoches
        for _ in range(3):
            ct = 0
            for sample in val_rd():
                ct += 1
                self.assertTrue(sample is not None)
            self.assertGreaterEqual(ct, coco._maxiter)

    def test_rcnn_train(self):
        """ Test reader for training
        """
        anno = self.rcnn_conf['DATA']['TRAIN']['ANNO_FILE']
        if not os.path.exists(anno):
            logging.error('exit test_rcnn for not found file[%s]' % (anno))
            return

        rcnn = Reader(self.rcnn_conf['DATA'], self.rcnn_conf['TRANSFORM'], 10)
        rcnn_rd = rcnn.train()
        self.assertTrue(rcnn_rd is not None)

        ct = 0
        out = None
        for sample in rcnn_rd():
            out = sample
            ct += 1
            self.assertTrue(sample is not None)
        self.assertEqual(out[0][0].shape[0], 3)
        self.assertEqual(out[0][1].shape[0], 3)
        self.assertEqual(out[0][3].shape[1], 4)
        self.assertEqual(out[0][4].shape[1], 1)
        self.assertEqual(out[0][5].shape[1], 1)
        self.assertGreaterEqual(ct, rcnn._maxiter)


if __name__ == '__main__':
    unittest.main()
