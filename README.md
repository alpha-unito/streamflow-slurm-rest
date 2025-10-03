# SLURM REST API Plugin for StreamFlow

## Installation
Simply install the package directory from [PyPI]() using [pip](https://pip.pypa.io/en/stable/). StreamFlow will automatically recognise it as a plugin and load it at each workflow execution.
```bash
pip install streamflow-slurm
```

If everything worked correctly, whenever a workflow execution start the following message should be printed in the log:
```bash
Successfully registered plugin streamflow.plugins.unito.slurmapi.plugin.SlurmApiStreamFlowPlugin
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

  slurm-api-deployment:
    type: unito.slurmapi
    config:
      services:
        slurm-api-service:
          api_address: <slurm_api_address>
          jwt_token: <jwt_token or path to jwt token file>
    wraps: ssh-deployment
```

The configuration for the deployment (service) follows that of the SLURM REST API for the /job/submit endpoint, and it is described in detail in the [official documentation](https://slurm.schedmd.com/rest_api.html). The only required fields are `api_address` and `jwt_token`.