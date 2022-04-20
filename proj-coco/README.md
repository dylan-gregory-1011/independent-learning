# Project Coco: Computer Vision

This project reflects the code & data reflecting to computer vision projects.  It currently is split into two different project initiatives.

1. **Object Detection within Coco:** This uses the standard coco datasets and annotations and familiarizes me with how to interact with the data, what the annotations reflect, good research on standardizing the process and other procedures.  [The data for this dataset was downloaded from here](https://viso.ai/computer-vision/coco-dataset/)
2. **CI Discount Project:** A parallel development of the [prior Kaggle Project CDI Image Classification](https://www.kaggle.com/c/cdiscount-image-classification-challenge) to be used as a pitch for future clients.


### Process:

1. Decide Image Annotation & Storage Format:  There are multiple different annotation types and formats to store as. [See this link for more information on annotations](https://towardsdatascience.com/image-data-labelling-and-annotation-everything-you-need-to-know-86ede6c684b1)

#### Annotation Types:

- **Bounding Boxes:** Bounding boxes are rectangular boxes used to define the location of the target object. They can be determined by the 𝑥 and 𝑦 axis coordinates in the upper-left corner and the 𝑥 and 𝑦 axis coordinates in the lower-right corner of the rectangle.
- **Polygonal Segmentation:** Complex polygons are used instead of rectangles to define the shape and location of the object in a much precise way.
- **Semantic Segmentation:** Pixel wise annotation, where every pixel in the image is assigned to a class. Semantic Segmentation is primarily used in cases where environmental context is very important. For example, it is used in self-driving cars and robotics because for the models to understand the environment they are operating in.
- **3D cuboids:** Similar to bounding boxes with additional depth information about the object. Thus, with 3D cuboids you can get a 3D representation of the object, allowing systems to distinguish features like volume and position in a 3D space.
- **Key-Point and Landmark:** Used to detect small objects and shape variations by creating dots across the image. This type of annotation is useful for detecting facial features, facial expressions, emotions, human body parts and poses.
- **Lines and Splines:** It is commonly used in autonomous vehicles for lane detection and recognition.

#### Annotation Formats:

- **COCO:** COCO has five annotation types: for object detection, keypoint detection, stuff segmentation, panoptic segmentation, and image captioning. The annotations are stored using JSON.
- **Pascal VOC:** Pascal VOC stores annotation in XML file. Below is an example of Pascal VOC annotation file for object detection.
- **YOLO:**  In YOLO labeling format, a .txt file with the same name is created for each image file in the same directory. Each .txt file contains the annotations for the corresponding image file, that is object class, object coordinates, height and width.

#### Viewing Sample Images:
To view the images and investigate the annotations overlaying the images, I used the python library pycoco and a jupyter notebook.  For sample code on how to do this [see the link](https://stackoverflow.com/questions/50805634/how-to-create-mask-images-from-coco-dataset)


2. Download Annotation tool for analysis.  For help deciding on what tool to use, [please see this link for annotation objects](https://neptune.ai/blog/annotation-tool-comparison-deep-learning-data-annotation)

- **Labelme:** [Link to Github Account](https://github.com/wkentaro/labelme)
- **MakeSense.ai:** [Link to Github account](https://github.com/SkalskiP/make-sense#:~:text=makesense.ai%20is%20a%20free,to%20be%20truly%20cross%2Dplatform.)

#### Labelme Example

```
labelme  # just open gui

# tutorial (single image example)
cd examples/tutorial
labelme apc2016_obj3.jpg  # specify image file
labelme apc2016_obj3.jpg -O apc2016_obj3.json  # close window after the save
labelme apc2016_obj3.jpg --nodata  # not include image data but relative image path in JSON file
labelme apc2016_obj3.jpg \
  --labels highland_6539_self_stick_notes,mead_index_cards,kong_air_dog_squeakair_tennis_ball  # specify label list

# semantic segmentation example
cd examples/semantic_segmentation
labelme data_annotated/  # Open directory to annotate all images in it
labelme data_annotated/ --labels labels.txt  # specify label list with a file 
```

#### MakeSense.ai

```
# clone repository
git clone https://github.com/SkalskiP/make-sense.git

# navigate to main dir
cd make-sense

# install dependencies
npm install

# serve with hot reload at localhost:3000
npm start
```

### Helpful Links:

- [Annotating Explained](https://www.v7labs.com/blog/image-annotation-guide)
- [Coco vs Pascal Visual Object Classes](https://towardsdatascience.com/coco-data-format-for-object-detection-a4c5eaf518c5)
- [Coco Annotations Explained](https://opencv.org/introduction-to-the-coco-dataset/)
- [Getting Started with COCO Notes](https://towardsdatascience.com/getting-started-with-coco-dataset-82def99fa0b8)
- [Coco Github Example](https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocoDemo.ipynb)

3. Preprocess & Store the data: For this project, we are chosing to convert all of the jpeg files to a hdf5 dataset to allow for batch iteration through the process and also optimize storage

- [Storage Considerations with Images](https://realpython.com/storing-images-in-python/)
- [Store data as HDF5](https://github.com/thushv89/PreprocessingBenchmarkDatasets/blob/master/preprocess_cifar.py)
- [Using Compressed HDF5](https://blade6570.github.io/soumyatripathy/hdf5_blog.html)

## OpenCV


## Computer Pipeline examples:
- [End to End Pipeline in 5 minutes](https://towardsdatascience.com/end-to-end-computer-vision-pipeline-in-5-minutes-e43e47a9c04a)

- [OpenCV Example Homepage](https://www.geeksforgeeks.org/opencv-python-tutorial/)
- [Image Processing Example](https://medium.com/analytics-vidhya/image-processing-using-opencv-cnn-and-keras-backed-by-tensor-flow-c9adf22bb271)


#### Future Datasets:
- [Coco Source Dataset]()
- [Github for Soccernet Project](https://github.com/SilvioGiancola/SoccerNetv2-DevKit)
- [Source for Youtube 8M Dataset](https://medium.com/google-cloud/youtube-8m-dataset-c2ee9c79d136)