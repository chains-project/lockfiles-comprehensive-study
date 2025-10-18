# Lockfiles Across Package Managers

This repository contains all the materials used and produced as part of our study "The Design Space of Lockfiles Across Package Managers".


## data/
This folder contains quantitative data mined from GitHub repositories, related to lockfile usage across different package managers.

Each JSON file corresponds to a specific package manager and includes the following information for each mined repository:

- Repository URL

- Approximate number of dependencies

- Project creation date

- Lockfile creation date

- A boolean flag (gap) indicating whether the lockfile was committed within six months of project creation

## scripts/
This folder contains the scripts used to mine the lockfiles from GitHub repositories. It has two sub-folders. 

 - lockfile-miner : Mines GitHub repositories that satisfy the conditions specified in search-config.json and use one of the seven package managers (npm CLI, pnpm, Cargo, Go, Gradle, Pipenv, or Poetry). It also checks whether a corresponding lockfile exists in each repository.
      - The default conditions are: 
        - 300 commits
        - 10 contributors
        - 42 stars
        - 2019-09-30 last creation date
 - filters: Filters out projects that do not specify any dependencies in the dependency configuration file.
    
The total number of collected projects and resulting projects after the filtering step is given below. 

|        | npm CLI | pnpm | Cargo | Go | Gradle | Pipenv | Poetry
| -------- | ------- | ------- | ------- | ------- | ------- | ------- | ------- |
| Total # of projects | 1922 | (1922) | 1089 | 1202 | 325 | 29 | 314 |
| # of projects with at least one dependency | 1916 | (1916) | 1089 | 1188 | 323 | 29 | 314 |


## developer_interviews/

This directory contains materials related to our qualitative interviews with developers:

- interview_protocol.pdf: The semi-structered interview protocols used during the interviews.

- invitation_email.pdf: The email templates used to invite participants.

- codebook.xlsx: The codebook.

## references/

This folder includes the supporting documentation and source code links used in the study.
