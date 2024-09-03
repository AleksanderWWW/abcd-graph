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
