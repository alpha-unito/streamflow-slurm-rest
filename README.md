# SLURM REST API Plugin for StreamFlow

## Installation 
<!-- **NOTE: not published on PyPI yet.**

Simply install the package directory from [PyPI]() using [pip](https://pip.pypa.io/en/stable/). StreamFlow will automatically recognise it as a plugin and load it at each workflow execution.
```bash
pip install streamflow-slurmrest
``` -->

Clone this repository and install the package directory using [pip](https://pip.pypa.io/en/stable/). StreamFlow will automatically recognise it as a plugin and load it at each workflow execution.
```bash
git clone https://github.com/alpha-unito/streamflow-slurm-rest
cd streamflow-slurm-rest
pip install .
```


If everything worked correctly, whenever a workflow execution start the following message should be printed in the log:
```bash
Successfully registered plugin streamflow.plugins.unito.slurmrest.plugin.SlurmRestStreamFlowPlugin
```

## Usage
```yml
deployments:
  ssh-deployment:
    type: ssh
    workdir: /path/to/workdir
    config:
      nodes:
        - 10.0.0.1
      sshKey: /path/to/ssh/key
      username: <username>

  slurm-rest-deployment:
    type: unito.slurmrest
    wraps: ssh-deployment
    config:
      api_address: <slurm_api_address> # Required
      api_version: v0.0.43  # Optional, default is v0.0.43
      jwt_token: <jwt_token or path to jwt token file> # Required
      services:
        slurm-rest-service:
          partition: <partition_name>
          <other_slurm_job_options>: <value>
          ...
```

The configuration for the service follows that of the SLURM REST API for the /job/submit endpoint, and it is described in detail in the [official documentation](https://slurm.schedmd.com/rest_api.html) (see [job configuration](https://slurm.schedmd.com/rest_api.html#v0.0.43_job_desc_msg)). All configuration options are optional, except for `api_address` and `jwt_token`.
