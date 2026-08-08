# Project Workflows

## Test
The test workflow is pretty straightforward, it simply triggers the pytest command which is os independent. For this 
workflow, I use ubuntu-latest because it is simplest.

## Release
When a release of stock bench is ready, a branch is created in the format “release/x.x.x”. When that branch is pushed 
to GitHub, the release workflow is triggered. A Windows Virtual machine is set up with Python set up on top of it. I 
have a custom build.py script as a part of the repository that is explicitly set up for versioning the executable in 
accordance with the name of the branch. This build scripts can be run locally and will build the executable on your 
machine. Instead of rebuilding this build script with a complex workflow, I simply have the workflow trigger the 
build.py file. Since the workflow runs in windows with Python setup, it builds just the same as it would on your 
local machine.