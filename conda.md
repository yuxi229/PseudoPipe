# Methods: Conda Package Development and Installation

## Package Structure and Metadata
The `meta.yaml` file was updated to define the package metadata, dependencies, and command-line entry points for PseudoPipe. The key addition was the `entry_points` section, which allows the installation to create accessible commands directly from the package.  
Example excerpt from `meta.yaml`:

```
entry_points:
  - pseudopipe-run = pseudopipe.cli:run_pipeline
  - pseudopipe-process = pseudopipe.cli:process_results
  - pseudopipe-results = pseudopipe.cli:view_results
```

This ensures that after installation, the user can execute `pseudopipe-run`, `pseudopipe-process`, and `pseudopipe-results` directly in the terminal without navigating into the package directory.

## Building the Conda Package
The package was built locally using the `conda-build` tool. Inside the package recipe directory (containing `meta.yaml`), the following command was executed:

```
conda build .
```

This command processed the recipe, resolved dependencies, and produced a `.tar.bz2` package file in the local conda build directory (e.g., `/home/user/miniconda3/conda-bld/`), ready for installation.

## Installing the Built Package
The locally built package was installed using:

```
conda install --use-local pseudopipe
```

The `--use-local` flag ensures that Conda searches the local build directory rather than pulling from an online channel.

## Verifying Installation
After installation, the new commands defined in `meta.yaml` were verified to be available system-wide by running:

```
pseudopipe-run --help
pseudopipe-process --help
pseudopipe-results --help
```

Successful output from these commands confirmed that the entry points were correctly set up.

## Summary
By defining explicit entry points in `meta.yaml` and using the local build-and-install workflow, PseudoPipe was packaged into a self-contained Conda environment with user-friendly commands for running, processing, and viewing results.
