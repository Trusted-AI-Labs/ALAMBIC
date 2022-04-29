---
layout: default
title: Installation
nav_order: 2
---

# Prerequisites

You need to have Docker, Docker compose and Git installed and know how to use the Terminal (at least a little bit).
[See here for Docker !](https://docs.docker.com/get-docker/)

# Installation
## 1. Clone the repository
In the terminal, navigate to the folder of your choice and then type

<div class="highlighter-rouge">
<code>
git clone https://github.com/cnachteg/ALAMBIC.git
</code>
</div>

## 2. Build the Docker
Go inside the GitHub repository newly created of ALAMBIC and type

<div class="highlighter-rouge">
<code>
docker-compose up
</code>
</div>

For the more expert, you can add options to that command ([see here](https://docs.docker.com/compose/reference/up/))

Note that you need to have all your data contained in the folder `data_alambic` situated on your user folder.

## 3. Launch the browser
You can find ALAMBIC at the adress <a href="http://0.0.0.0:8000/" target="_blank">http://0.0.0.0:8000/</a> !

# Shutdown
You can stop the docker and flush the database of all the data and results by typing in the terminal

<div class="highlighter-rouge">
<code>
docker-compose down -v
</code>
</div>
