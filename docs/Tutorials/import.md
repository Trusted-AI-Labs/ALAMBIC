---
layout: default 
title: Import the Data 
parent: How to use ALAMBIC 
nav_order: 1
---
<details close markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

# Overview
The import of data in the database depends on the type of the data and the task we want the model to execute afterwards. Everything will be uploaded according to a `.tsv` file with a specific format which will be further explained in the following sections.

To import the data, from the home page click on `Upload data` on the upper left corner or got directly to <a href="http://0.0.0.0:8000/upload" target="_blank">http://0.0.0.0:8000/upload</a>

![](../assets/images/homepage_upload.png)
{: .text-center }

On the Upload page, you can select the task and the type of data you manage. You also have to select in the dropdown menu the `.tsv` file with the desired format which will be use for the import.

![](../assets/images/pouring.png)

<p><p class="label label-red">Important</p> All the data you want to upload MUST BE in the `data_alambic` folder before you build the docker-compose and mount the volumes ! </p>

# Classification
## For text & 2D images
{: .no_toc }

The `.tsv` file has two columns, named `file` and `label`, with a line for each sample such as :

| file | label |
|:---:|:---:|
| relative path where the file is situated with `data_alambic` as the working directory | class label of the data |

<h1>Relation Extraction <p class='label label-yellow'>Coming soon</p></h1>