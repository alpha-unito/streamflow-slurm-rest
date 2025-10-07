# SLURM REST API Plugin for StreamFlow

## Installation 
**NOTE: not published on PyPI yet.**

Simply install the package directory from [PyPI]() using [pip](https://pip.pypa.io/en/stable/). StreamFlow will automatically recognise it as a plugin and load it at each workflow execution.
```bash
pip install streamflow-slurmrest
```

If everything worked correctly, whenever a workflow execution start the following message should be printed in the log:
```bash
Successfully registered plugin streamflow.plugins.unito.slurmrest.plugin.SlurmRestStreamFlowPlugin
```

## Usage
This plugin registers a new `Connector` component, called `SLURMConnector`, which extends the StreamFlow `ConnectorWrapper` class. This implies that the `SLURMConnector` can wrap an underlying `Connector` object through the `wraps` directive. The example below shows a possible `streamflow.yml` configuration file, where the `SLURMConnector` wraps an `SSHConnector` for remote execution offloading.

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
    config:
      api_address: <slurm_api_address>
      api_version: v0.0.43  # Optional, default is v0.0.43
      jwt_token: <jwt_token or path to jwt token file>
      services:
        slurm-rest-service:
          partition: <partition_name>
          <other_slurm_job_options>: <value>
    wraps: ssh-deployment
```

The configuration for the deployment (service) follows that of the SLURM REST API for the /job/submit endpoint, and it is described in detail in the [official documentation](https://slurm.schedmd.com/rest_api.html). The only required fields are `api_address` and `jwt_token`.