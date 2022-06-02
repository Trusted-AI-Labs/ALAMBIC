# ALAMBIC
ALAMBIC, or **A**ctive **L**earning **A**utomation with **M**ethods to **B**attle **I**nsufficient **C**uration, is an open-source Dockerized web platform for the study
and development of machine learning models with the help of active learning.

## Documentation
Available on https://trusted-ai-labs.github.io/ALAMBIC/

## Installation
## 1. Clone the repository
In the terminal, navigate to the folder of your choice and then type

```
git clone https://github.com/cnachteg/ALAMBIC.git
```

## 2. Build the Docker
Go inside the GitHub repository newly created of ALAMBIC and type

```
docker-compose up
```

For the more expert, you can add options to that command ([see here](https://docs.docker.com/compose/reference/up/))

Note that you need to have all your data contained in the folder `data_alambic` situated in your user directory.

## 3. Launch the browser
You can find ALAMBIC at the adress <a href="http://0.0.0.0:8000/" target="_blank">http://0.0.0.0:8000/</a> !

# Shutdown
You can stop the docker and flush the database of all the data and results by typing in the terminal

```
docker-compose down -v
```

## Acknowledgements
This project was realised at the <a href="http://ibsquare.be" target="_blank"><span class="ltf">Interuniversity Institute of Bioinformatics in Brussels (IB2)</a>, a collaborative
bioinformatics research initiative between Université Libre de Bruxelles (ULB) and Vrije Universiteit Brussel (VUB).
Basic architecture and design was largely inspired by the work done by Alexandre Renaux for ORVAl (<a href="https://orval.ibsquare.be" target="_blank"><span class="ltf">https://orval.ibsquare.be</span></a>).
This work was supported by Service Public de Wallonie Recherche under grant n° 2010235 -ARIAC by DIGITALWALLONIA4.AI.

## License
This work is under a BSD-3-Clause license.

## Cite us
See above by clicking on "Cite this repository"