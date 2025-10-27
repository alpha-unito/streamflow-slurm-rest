**Distributed Example Workflow**
The `local` workflow uses the SLURM REST API to launch the `hpc` workflow on a distributed cluster.

**Requirements**
- the `hpc` workflow must be available on the cluster
- the `streamflow` package must be installed on the cluster or accessible via a container/venv/...
- `/local/inputs.yml > streamflow_path` must point to the `streamflow` installation on the cluster
- `/local/inputs.yml > streamflow_workflow` must point to the `hpc/streamflow.yml` straemflow file on the cluster

**Running the Example**
- Copy the `hpc` workflow to the cluster if not already available
- Adjust the `/local/inputs.yaml` file to point to the correct `streamflow` installation and `hpc` workflow on the cluster
- Install the plugin if not already done:
  ```bash
  pip install .
  ```
- From the `examples/distributed/local` directory, run:
  ```bash
  streamflow run streamflow.yml
  ```

**Notes**
- The CWL steps `step_1` and `step_3` are executed on the local machine and can be exchanged to any other CWL workflow.
- The CWL step `step_2` launches the `hpc` workflow on the cluster via the SLURM REST API.
- The inputs and outputs from and to `step_2` are used for dependency only, data transfer cannot be performed using the SLURM REST API.