# Introduction 
This repository represents a collection of independent learning activities that help up-skill and learn different Machine Learning and AI specialties.  All of these initiatives have been executed on a desktop computer and follows the below structure with large directories ignored when considered for git. For an explanation of the projects, please consult the overviews below, the README files in each subdirectory or the documents under each file.


# Project Bard (Shakespeare Next Sentance Prediction)
For the pinnacle of english communication, one needs to look no further than the bard, otherwise known as William Shakespeare.  This project looks to use current language translations of shakespeare's play to create a model that can reply to any delcaration with old english texts.  Deconstructing language into a mathmatical representation so that it can feed a generalizable model requires an understanding of both individual words and the flow of ideas.  Accomplishing this with State of the Art transformers reflects current best practices in the industry and this project will hopefully build on these approaches and improve long-term idea connectivity.


For more information, please see the [README file for this project](proj-bard/README.md)

# Project Amazon (Reinforcement Learning)



For more information, please see the [README file for this project](proj-amazon/README.md)


# Project Satellite (Geospatial Machine Learning)



For more information, please see the [README file for this project](proj-satellite/README.md)


# Project Osmosis



For more information, please see the [README file for this project](proj-osmosis/README.md)


# Project Coco



For more information, please see the [README file for this project](proj-coco/README.md)


## Directory Structure

```
|-- data
|    |-- amazon
|    |-- bard
|    |-- coco
|    |-- osmosis
|    |-- satellite
|-- keys
|    |-- aws-root-key.csv
|-- proj-amazon
|   |-- bin
|   |-- docs
|   |-- src
|   |-- unit_tests
|-- proj-bard
|   |-- bin
|   |-- docs
|   |-- src
|   |-- unit_tests
|-- proj-coco
|   |-- bin
|   |-- docs
|   |-- src
|   |-- unit_tests
|-- proj-osmosis
|   |-- bin
|   |-- docs
|   |-- src
|   |-- unit_tests
|-- proj-satellite
|   |-- bin
|   |-- docs
|   |-- src
|   |-- unit_tests
```

# Getting Started
TODO: Guide users through getting your code up and running on their own system. In this section you can talk about:
1.	Installation process
2.	Software dependencies
3.	Latest releases
4.	API references

# Build and Test


# Contributers
These project reflects the individual projects undertaken by Dylan Smith and are not to be used in any other capacity.

If you want to learn more about creating good readme files then refer the following [guidelines](https://docs.microsoft.com/en-us/azure/devops/repos/git/create-a-readme?view=azure-devops). You can also seek inspiration from the below readme files:
- [ASP.NET Core](https://github.com/aspnet/Home)
- [Visual Studio Code](https://github.com/Microsoft/vscode)
- [Chakra Core](https://github.com/Microsoft/ChakraCore)
- [Github Example](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)

#### Setting up Conda Environments

```
conda create -n bard python=3.8
conda activate bard

```

- [Conda Examples](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/)


#### Creating a requirements.txt file


```
python -m pip freeze > requirements.txt
```

- [Pip Freeze](https://pip.pypa.io/en/stable/cli/pip_freeze/)


#### Catching up Feature Branch to main 

```
git rebase main
```

- [Sample Rebase](https://belev.dev/git-merge-vs-rebase-to-keep-feature-branch-up-to-date)