# Overview of Computer Vision Topics

## 1. Image Classification

#### Overview:
 
Takes an image and using the different features of each image predicts the labeled class.  This follows mostly the paradigm of standard multi-class or binary classification. Covolutional Network layers build feature maps from the input, combine these maps through sub-sampling and pooling and then can be used to feed through to a classification algorithm that is represented more similarly through dense layers.  Our process used feature extraction to add a new classifier on top of the pretrained model to reuse the feature maps.

#### Sample Format

- **Input:** An image with a single object, such as a photograph.
- **Output:** A class label (e.g. one or more integers that are mapped to class labels).

#### Important Convolutional Neural Network Steps (CNN):

1. **Filter Size:** This directly impacts the size of the kernel and is typically 2, 3 or 4.
2. **Padding:** Allows the filter to slide through the image, generates an output feature map of the desired size.
3. **Stride:** The number of pixes to increment by (1 means to move over by one pixel for each calculation).  Increasing stride reduces the size of the output
4. **Channels:**  Increased depth of colors makes more complex pictures but it also allows the process to see all the colors 
5. **Pooling:** This is a sub sampling operation that reduces the size of feature maps by summarizing sub-regions, such as average or the maximum value *(max pooling)*.  This reduces the dependecy of the feature vectors on their exact placement in an image.  These layers do not do any learning themselves, it instead reduces the size of the problem by introducing sparseness.
6. **Back Propogation:** CNNs train using back-prop 
7. **Batch Normalization:** This speeds up training of Deep Networks and stabilizes the process.  It consists of normalizing the activation vectors from the hidden layers using the first and second statistical moments (mean and variance) of the current batch.

#### Best Practices:

- Add batch normalization to prevent overfitting. [Batch Normalization Explained in more detail](https://towardsdatascience.com/batch-normalization-in-3-levels-of-understanding-14c2da90a338)
- Train with multiple image orientations and noise
- Train on GPUs and use BLAS libraries
- [Convolutional Neural Networks for Image Classification Explained](https://www.analyticsvidhya.com/blog/2021/08/image-classification-using-cnn-understanding-computer-vision/)

## Object Detection

#### Overview: 

Locate the presence of objects with a bounding box and types or classes of the located objects in an image.  Algorithms produce a list of object categories present in the image along with an axis-aligned bounding box indicating the position and scale of every instance of each object category. [For an example of Object Detection, please see this link](https://machinelearningmastery.com/object-recognition-with-deep-learning/)

#### Sample Format:

- **Input:** An image with one or more objects, such as a photograph.
- **Output:** One or more bounding boxes (e.g. defined by a point, width, and height), and a class label for each bounding box.

#### Notes:

- You may observe that some objects have been detected multiple times and we have more than one bounding box for it. To fix this situation we’ll need to apply Non-Maximum Suppression (NMS), also called Non-Maxima Suppression. We pass in confidence threshold value and NMS threshold value as parameters to select one bounding box. From the range of 0 to 1, we should select an intermediate value like 0.4 or 0.5 to make sure that we detect the overlapping objects but do not end up getting multiple bounding boxes for the same object.

## Instance Segmentation 

#### Overview: 

This refers to the process of grouping pixels in an image in a simantically meaningful way (i.e. grouping objects) This process
is more specific than object detection or classification because the predictions are at a more granular level then document / bounding box
value. [Mask-R CNN is a good approach for handling this](https://towardsdatascience.com/computer-vision-instance-segmentation-with-mask-r-cnn-7983502fcad1)


## Tracking Algorithms 

**Object Tracking:** Object tracking is the process of locating a moving object in a video. You can consider an example of a football match. You have a live feed of the match going on and your task is to track the position of the ball at every moment. The task seems simple for an average human but it’s way too complex for even the smartest machine. [This has been already implemented at different clients](https://viso.ai/deep-learning/object-tracking/)

**OpenCV Object Tracking:**  This is a popular method because OpenCV has so many algorithms built-in that are specifically optimized for the needs and objectives of object or motion tracking.Specific Open CV object trackers include the BOOSTING, MIL, KCF, CSRT, MedianFlow, TLD, MOSSE, and GOTURN trackers. Each of these trackers is best for different goals. For example, CSRT is best when the user requires a higher object tracking accuracy and can tolerate slower FPS throughput. For examples of how this is used with OpenCV, please consult [this link](https://pyimagesearch.com/2018/07/30/opencv-object-tracking/) or [this link](https://www.analyticsvidhya.com/blog/2021/08/getting-started-with-object-tracking-using-opencv/)

The selection of an OpenCV object tracking algorithm depends on the advantages and disadvantages of that specific tracker and the benefits:
- The KCF tracker is not as accurate compared to the CSRT but provides comparably higher FPS.
- The MOSSE tracker is very fast, but its accuracy is even lower than tracking with KCF. Still, if you are looking for the fastest object tracking OpenCV method, MOSSE is a good choice.
- The GOTURN tracker is the only detector for deep learning based object tracking with OpenCV. The original implementation of GOTURN is in Caffe, but it has been ported to the OpenCV Tracking API.


## Common Algorithms 

#### Important Steps and Considerations:
- In order to use transfer learning appropriately, you must freeze different layers of the pretrained weights to not lose the benefitsof the prior models and to fine tune to the performance of the models.  With the proper layers frozen, add trainable layers to help with predictiors.
- Base layer training

## Popular Models and Links

There are multiple different pre-trained models where you can use pre-loaded feature mapes.  For a comparison of these use cases, [please see this link](https://analyticsindiamag.com/a-comparison-of-4-popular-transfer-learning-models/) and for sample datasets to be used in future projects, [please see this link](https://towardsai.net/p/computer-vision/50-object-detection-datasets-from-different-industry-domains)

1. **(GoogLeNet) Inception::** - Currently in the third version
    - [A Simple Guide to Inception](https://towardsdatascience.com/a-simple-guide-to-the-versions-of-the-inception-network-7fc52b863202)
    - [The Keras Documentation of InceptionV3](https://www.tensorflow.org/api_docs/python/tf/keras/applications/inception_v3/InceptionV3)
    - [A Sample Implementation of InceptionV3 for Image Classification](https://medium.com/analytics-vidhya/transfer-learning-using-inception-v3-for-image-classification-86700411251b)

2. **Xception:**
    - [A Keras example of running xception](https://neptune.ai/blog/transfer-learning-guide-examples-for-images-and-text-in-keras)
    - [How to use transfer learning with CNNs](https://machinelearningmastery.com/how-to-use-transfer-learning-when-developing-convolutional-neural-network-models/)
3. **ResNet50**
4. **VGG19**
5. **YoloV3 Algorithm:** Comes in a preloaded function or something that can be custom trained.. Yolo can run predictions simultaneously in a single stage approach while Faster R-CNN typically uses a two stage approach
    - [](https://towardsdatascience.com/object-detection-using-yolov3-and-opencv-19ee0792a420
    - [](https://neptune.ai/blog/object-detection-with-yolo-hands-on-tutorial
    - [](https://opencv-tutorial.readthedocs.io/en/latest/yolo/yolo.html
6. **MobileNet V2**
7. **Mask R-CNN:** This model is divided into two parts, one that comprises of a region proposal network to propose candidate objects in every box and a binary mask classifier to generate a mask for every class.  The image is run through a CNN to generate feature maps while the RPN generates multiple RoI using a lightweight binary classifier.  The RoI Align network outputs multiple bounding boxes rather than a single definite one and warped them to use a fixed dimension.Warped features are then fed into fully connected layers to make classification using softmax and boundary box prediction is further refined using the regression model. Warped features are then fed into fully connected layers to make classification using softmax and boundary box prediction is further refined using the regression model.

## Image Preprocessing Steps

1. Determine the benefit of color to an image, and whether to have a multi-channel implementation or a single channel approach.
2. Standardize the image through resizing and normalizing the individual values in each channel.
3. Increase training dataset through data-augmentation methods such as scaling, rotations or other affine transformations.
4. Reduce Noise and enhance images. In OpenCV there are multiple ways to denoise the data and each is specific to the number of channels in the input image. (NlMeansDenoising)
5. Thresholding. You can either use adaptive thresholding or global thresholding.  Adaptive thresholding focuses on using local areas and is much betterthen global methedology.  Different thresholds for different regions gives better results for varying illumination.
6. Filtering scans for borders between different colors and so can detect contours of objects.
