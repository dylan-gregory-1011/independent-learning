##!/usr/bin/env python
"""


"""

from pathlib import Path
import cv2
import glob
import json
import fiftyone as fo

__author__ = "Dylan Smith"
__copyright__ = "Copyright (C) 2022 Dylan Smith"
__credits__ = ["Dylan Smith"]

__license__ = "Personal Use"
__version__ = "1.0"
__maintainer__ = "Dylan Smith"
__email__ = "-"
__status__ = "Development"

# Constants
PROJ = Path(__file__).resolve().parent.parent.parent
RAW_DATA = PROJ.joinpath('data','coco','raw')
ANNOTATION_DATA = PROJ.joinpath('data','coco','raw','annotations')
PROC_DATA = PROJ.joinpath('data','coco', 'processed')


def displayFiles(path):
    '''
    
    '''
    p = path.glob('**/*')
    files = [x for x in p if x.is_file()]

    for file in files:
        # Read the image from the file
        img = cv2.imread(str(file), cv2.IMREAD_COLOR)

        # Display the image
        cv2.imshow("Dylan's First Image", img)

        # To hold the window on screen, we use cv2.waitKey method
        cv2.waitKey(0)
        
        # It is for removing/deleting created GUI window from screen and memory
        cv2.destroyAllWindows()
        break
    print(len(files))


def convertToCocoDataset(img_typ, anno_typ):
    '''
    A function to conver the coco dataset to a fifty-one readable dataset
    ...
    Parameters
    ----------
    img_typ:
    anno_typ:
    '''
    # load the annotations file
    with open(ANNOTATION_DATA.joinpath('%s_%s2017.json' % (anno_typ,img_typ)), 'r') as json_file:
        annotations = json.load(json_file)

        # Define annotations as the annotation dict
        annotations_ = annotations['annotations']
        images_ = annotations['images']

    # Define the dataset name
    data_nm = '%s-%s-dataset' %(anno_typ,img_typ)

    # If the dataset already exists, delete
    if data_nm in fo.list_datasets():
        dataset = fo.load_dataset(data_nm)
        dataset.delete()

    # Create the new dataset
    dataset = fo.Dataset(name= data_nm)

    # Persist the dataset on disk in order to be able to load it in one line in the future
    dataset.persistent = True

    # Get the data
    p = RAW_DATA.joinpath('%s2017' % img_typ).glob('**/*')
    files = [x for x in p if x.is_file()]

    for filepath in files:
        sample = fo.Sample(filepath=filepath)

        # Convert detections to FiftyOne format
        detections = []
        for obj in annotations_[filepath]:
            label = obj["label"]

            # Bounding box coordinates should be relative values
            # in [0, 1] in the following format: [top-left-x, top-left-y, width, height]
            bounding_box = obj["bbox"]

            detections.append(
                fo.Detection(label=label, bounding_box=bounding_box)
            )

        # Store detections in a field name of your choice
        sample["ground_truth"] = fo.Detections(detections=detections)

        dataset.add_sample(sample)
    
    export_dir = PROC_DATA.joinpath('%s_%s2017' % (img_typ, anno_typ))
    label_field = "ground_truth"  # for example

    # Export the dataset
    dataset.export(
        export_dir=export_dir,
        dataset_type=fo.types.COCODetectionDataset,
        label_field=label_field,
    )

def main():
    '''
    
    '''
    print('Missing')
    #displayFiles(path = TRAIN_DATA)


if __name__ == '__main__':
    #main()
    convertToCocoDataset(img_typ = 'val', anno_typ = 'instances') 