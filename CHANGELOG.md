## abcd-graph 0.4.1

### Changes
- Reduced docker image size with multi-stage build ([#62](https://github.com/AleksanderWWW/abcd-graph/pull/62))


## abcd-graph 0.4.0

### Fixes
- Fixed calculating expected community cdf ([#48](https://github.com/AleksanderWWW/abcd-graph/pull/48))
- Fixed build crashing with integer beta and gamma values ([#48](https://github.com/AleksanderWWW/abcd-graph/pull/48))

### Changes
- Made property computation lazy ([#45](https://github.com/AleksanderWWW/abcd-graph/pull/45))

### Enhancements
- Sped up building `Xi matrix` by pre-computing community volumes and empirical xi's ([#47](https://github.com/AleksanderWWW/abcd-graph/pull/47))

### Features
- Allowed to pass custom degree and community size sequences ([#57](https://github.com/AleksanderWWW/abcd-graph/pull/57))


## abcd-graph 0.3.0

### Misc
- Added an example of using the library in a Jupyter notebook ([#29](https://github.com/AleksanderWWW/abcd-graph/pull/29))

### Features
- Improved `Dockerfile` and added option to install additional packages during image build ([#28](https://github.com/AleksanderWWW/abcd-graph/pull/28))
- Added a top-level `ABCDCommunity` class to represent user-facing community properties ([#31](https://github.com/AleksanderWWW/abcd-graph/pull/31))
- Added a method to retrieve membership list for the graph ([#34](https://github.com/AleksanderWWW/abcd-graph/pull/34))
- Added ground truth community property to exported graph attributes ([#34](https://github.com/AleksanderWWW/abcd-graph/pull/34))
- Added outlier generation to the graph ([#36](https://github.com/AleksanderWWW/abcd-graph/pull/36))

### Breaking Changes
- Renamed the top level graph object from `Graph` to `ABCDGraph` ([#31](https://github.com/AleksanderWWW/abcd-graph/pull/31))
- Made retrieving edge and community lists the responsibility of the `ABCDGraph` object ([#31](https://github.com/AleksanderWWW/abcd-graph/pull/31))
- Change `ABCDParams` arguments and get rid of pydantic ([#36](https://github.com/AleksanderWWW/abcd-graph/pull/36))
- Include number of vertices and number of outliers to the params ([#36](https://github.com/AleksanderWWW/abcd-graph/pull/36))


## abcd-graph 0.2.1


## abcd-graph 0.2.0

### Features
- Added exporting the graph to `scipy.csr_matrix` ([#16](https://github.com/AleksanderWWW/abcd-graph/pull/16))
- Added a function to set the random seed ([#17](https://github.com/AleksanderWWW/abcd-graph/pull/17))
- Expose method to list communities' edges ([#18](https://github.com/AleksanderWWW/abcd-graph/pull/18))
- Add exporting graph to vector of pairs ([#19](https://github.com/AleksanderWWW/abcd-graph/pull/19))
- Added empirical xi (global and per community) to diagnostics ([#20](https://github.com/AleksanderWWW/abcd-graph/pull/20))
- Added `degree_sequence` property calculated from edge list ([#20](https://github.com/AleksanderWWW/abcd-graph/pull/20))
- Implemented callback mechanism to handle diagnostics and visualization ([#23](https://github.com/AleksanderWWW/abcd-graph/pull/23))
- Added visualization of CDF of community sizes and degrees ([#23](https://github.com/AleksanderWWW/abcd-graph/pull/23))

### Changes
- Restructured the project to have a more consistent API ([#23](https://github.com/AleksanderWWW/abcd-graph/pull/23))
- Renamed env variable controlling logging level to `ABCD_LOG` ([#23](https://github.com/AleksanderWWW/abcd-graph/pull/23))
