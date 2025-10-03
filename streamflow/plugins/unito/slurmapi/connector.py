from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import shlex
from collections.abc import Collection, MutableMapping, MutableSequence
from functools import partial
from importlib.resources import files
from typing import Any, cast
import requests

import cachetools

from streamflow.core.asyncache import cachedmethod
from streamflow.core.deployment import ExecutionLocation
from streamflow.deployment.connector.queue_manager import (
    QueueManagerConnector,
    QueueManagerService,
)
from streamflow.log_handler import logger


EXCLUDED_SERVICE_PARAMETERS = [
    "jwt_token",
    "api_address",
    "api_version",
]


def _slurmapi_request(
    method: str,
    url: str,
    jwt_token: str,
    headers: dict[str, str] | None = None,
    **kwargs: Any,
) -> requests.Response:
    if headers is None:
        headers = {}
    headers["X-SLURM-USER-TOKEN"] = jwt_token
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            f"""
▶️  SLURM API Request:
        Method: {method}
        URL: {url}
        Headers: {headers}
        Payload: {json.dumps(kwargs, indent=4) if kwargs else None}
"""
        )

    response = requests.request(method, url, headers=headers, **kwargs)

    if response.status_code != 200 or response.json().get("error"):
        errors = response.json().get("errors", [])
        for e in errors:

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    f"""
‼️  Error with SLURM API:
    {method} | {url}
    Headers: {headers}
    Payload: {json.dumps(kwargs, indent=4) if kwargs else None}
    Response Code: {response.status_code}
"""
                )
            else:
                logger.error(
                    f"‼️  Error with SLURM API: {e.get('error')} ({e.get('description')})"
                )

    return response


class SlurmApiService(QueueManagerService):
    def __init__(
        self,
        jwt_token: str,
        api_address: str,
        api_version: str = "v0.0.43",
        account: str | None = None,
        account_gather_frequency: str | None = None,
        admin_comment: str | None = None,
        allocation_node_list: str | None = None,
        allocation_node_port: int | None = None,
        argv: list[str] | None = None,
        array: str | None = None,
        batch_features: str | None = None,
        begin_time: int | None = None,
        flags: list[str] | None = None,
        burst_buffer: str | None = None,
        clusters: str | None = None,
        cluster_constraint: str | None = None,
        comment: str | None = None,
        contiguous: bool | None = None,
        container: str | None = None,
        container_id: str | None = None,
        core_specification: int | None = None,
        thread_specification: int | None = None,
        cpu_binding: str | None = None,
        cpu_binding_flags: list[str] | None = None,
        cpu_frequency: str | None = None,
        cpus_per_tres: str | None = None,
        crontab: Any = None,
        deadline: int | None = None,
        delay_boot: int | None = None,
        dependency: str | None = None,
        end_time: int | None = None,
        environment: list[str] | None = None,
        rlimits: Any = None,
        excluded_nodes: list[str] | None = None,
        extra: str | None = None,
        constraints: str | None = None,
        group_id: str | None = None,
        hetjob_group: int | None = None,
        immediate: bool | None = None,
        job_id: int | None = None,
        kill_on_node_fail: bool | None = None,
        licenses: str | None = None,
        mail_type: list[str] | None = None,
        mail_user: str | None = None,
        mcs_label: str | None = None,
        memory_binding: str | None = None,
        memory_binding_type: list[str] | None = None,
        memory_per_tres: str | None = None,
        name: str | None = None,
        network: str | None = None,
        nice: int | None = None,
        tasks: int | None = None,
        oom_kill_step: int | None = None,
        open_mode: list[str] | None = None,
        reserve_ports: int | None = None,
        overcommit: bool | None = None,
        partition: str | None = None,
        distribution_plane_size: Any = None,
        power_flags: list[Any] | None = None,
        prefer: str | None = None,
        hold: bool | None = None,
        priority: Any = None,
        profile: list[str] | None = None,
        qos: str | None = None,
        reboot: bool | None = None,
        required_nodes: list[str] | None = None,
        requeue: bool | None = None,
        reservation: str | None = None,
        script: str | None = None,
        shared: list[str] | None = None,
        site_factor: int | None = None,
        spank_environment: list[str] | None = None,
        distribution: str | None = None,
        time_limit: Any = None,
        time_minimum: Any = None,
        tres_bind: str | None = None,
        tres_freq: str | None = None,
        tres_per_job: str | None = None,
        tres_per_node: str | None = None,
        tres_per_socket: str | None = None,
        tres_per_task: str | None = None,
        user_id: str | None = None,
        wait_all_nodes: bool | None = None,
        kill_warning_flags: list[str] | None = None,
        kill_warning_signal: str | None = None,
        kill_warning_delay: Any = None,
        current_working_directory: str | None = None,
        cpus_per_task: int | None = None,
        minimum_cpus: int | None = None,
        maximum_cpus: int | None = None,
        nodes: str | None = None,
        minimum_nodes: int | None = None,
        maximum_nodes: int | None = None,
        minimum_boards_per_node: int | None = None,
        minimum_sockets_per_board: int | None = None,
        sockets_per_node: int | None = None,
        threads_per_core: int | None = None,
        tasks_per_node: int | None = None,
        tasks_per_socket: int | None = None,
        tasks_per_core: int | None = None,
        tasks_per_board: int | None = None,
        ntasks_per_tres: int | None = None,
        minimum_cpus_per_node: int | None = None,
        memory_per_cpu: Any = None,
        memory_per_node: Any = None,
        temporary_disk_per_node: int | None = None,
        selinux_context: str | None = None,
        required_switches: Any = None,
        segment_size: Any = None,
        standard_error: str | None = None,
        standard_input: str | None = None,
        standard_output: str | None = None,
        wait_for_switch: int | None = None,
        wckey: str | None = None,
        x11: list[str] | None = None,
        x11_magic_cookie: str | None = None,
        x11_target_host: str | None = None,
        x11_target_port: int | None = None,
    ):
        super().__init__()
        self.jwt_token = jwt_token
        self.api_address = api_address
        self.api_version = api_version

        self.account = account
        self.account_gather_frequency = account_gather_frequency
        self.admin_comment = admin_comment
        self.allocation_node_list = allocation_node_list
        self.allocation_node_port = allocation_node_port
        self.argv = argv
        self.array = array
        self.batch_features = batch_features
        self.begin_time = begin_time
        self.flags = flags
        self.burst_buffer = burst_buffer
        self.clusters = clusters
        self.cluster_constraint = cluster_constraint
        self.comment = comment
        self.contiguous = contiguous
        self.container = container
        self.container_id = container_id
        self.core_specification = core_specification
        self.thread_specification = thread_specification
        self.cpu_binding = cpu_binding
        self.cpu_binding_flags = cpu_binding_flags
        self.cpu_frequency = cpu_frequency
        self.cpus_per_tres = cpus_per_tres
        self.crontab = crontab
        self.deadline = deadline
        self.delay_boot = delay_boot
        self.dependency = dependency
        self.end_time = end_time
        self.environment = environment
        self.rlimits = rlimits
        self.excluded_nodes = excluded_nodes
        self.extra = extra
        self.constraints = constraints
        self.group_id = group_id
        self.hetjob_group = hetjob_group
        self.immediate = immediate
        self.job_id = job_id
        self.kill_on_node_fail = kill_on_node_fail
        self.licenses = licenses
        self.mail_type = mail_type
        self.mail_user = mail_user
        self.mcs_label = mcs_label
        self.memory_binding = memory_binding
        self.memory_binding_type = memory_binding_type
        self.memory_per_tres = memory_per_tres
        self.name = name
        self.network = network
        self.nice = nice
        self.tasks = tasks
        self.oom_kill_step = oom_kill_step
        self.open_mode = open_mode
        self.reserve_ports = reserve_ports
        self.overcommit = overcommit
        self.partition = partition
        self.distribution_plane_size = distribution_plane_size
        self.power_flags = power_flags
        self.prefer = prefer
        self.hold = hold
        self.priority = priority
        self.profile = profile
        self.qos = qos
        self.reboot = reboot
        self.required_nodes = required_nodes
        self.requeue = requeue
        self.reservation = reservation
        self.script = script
        self.shared = shared
        self.site_factor = site_factor
        self.spank_environment = spank_environment
        self.distribution = distribution
        self.time_limit = time_limit
        self.time_minimum = time_minimum
        self.tres_bind = tres_bind
        self.tres_freq = tres_freq
        self.tres_per_job = tres_per_job
        self.tres_per_node = tres_per_node
        self.tres_per_socket = tres_per_socket
        self.tres_per_task = tres_per_task
        self.user_id = user_id
        self.wait_all_nodes = wait_all_nodes
        self.kill_warning_flags = kill_warning_flags
        self.kill_warning_signal = kill_warning_signal
        self.kill_warning_delay = kill_warning_delay
        self.current_working_directory = current_working_directory
        self.cpus_per_task = cpus_per_task
        self.minimum_cpus = minimum_cpus
        self.maximum_cpus = maximum_cpus
        self.nodes = nodes
        self.minimum_nodes = minimum_nodes
        self.maximum_nodes = maximum_nodes
        self.minimum_boards_per_node = minimum_boards_per_node
        self.minimum_sockets_per_board = minimum_sockets_per_board
        self.sockets_per_node = sockets_per_node
        self.threads_per_core = threads_per_core
        self.tasks_per_node = tasks_per_node
        self.tasks_per_socket = tasks_per_socket
        self.tasks_per_core = tasks_per_core
        self.tasks_per_board = tasks_per_board
        self.ntasks_per_tres = ntasks_per_tres
        self.minimum_cpus_per_node = minimum_cpus_per_node
        self.memory_per_cpu = memory_per_cpu
        self.memory_per_node = memory_per_node
        self.temporary_disk_per_node = temporary_disk_per_node
        self.selinux_context = selinux_context
        self.required_switches = required_switches
        self.segment_size = segment_size
        self.standard_error = standard_error
        self.standard_input = standard_input
        self.standard_output = standard_output
        self.wait_for_switch = wait_for_switch
        self.wckey = wckey
        self.x11 = x11
        self.x11_magic_cookie = x11_magic_cookie
        self.x11_target_host = x11_target_host
        self.x11_target_port = x11_target_port


class SlurmApiConnector(QueueManagerConnector):
    @classmethod
    def get_schema(cls) -> str:
        return (
            files(__package__)
            .joinpath("schemas")
            .joinpath("slurmapi.json")
            .read_text("utf-8")
        )

    def _get_service(self, location: ExecutionLocation) -> SlurmApiService:
        if location.service not in self.services:
            raise ValueError(f"‼️  Service {location.service} not found")
        return cast(SlurmApiService, self.services.get(location.service))

    def _get_jwt_token(self, location: ExecutionLocation) -> str:
        service = self._get_service(location)

        # token can be a path or the token itself
        if os.path.exists(service.jwt_token):
            with open(service.jwt_token, "r") as f:
                return f.read().strip()
        else:
            return service.jwt_token

    # TODO: implement getting output from slurm api
    async def _get_output(self, job_id: str, location: ExecutionLocation) -> str:
        raise NotImplementedError(
            "‼️ Getting output from Slurm API is not implemented yet"
        )

    async def _get_returncode(self, job_id: str, location: ExecutionLocation) -> int:
        service = self._get_service(location)

        r = _slurmapi_request(
            "GET",
            f"{service.api_address}/slurm/{service.api_version}/job/{job_id}",
            self._get_jwt_token(location),
        )

        return_code = f"{r.json().get('jobs')[0].get('exit_code').get('return_code').get('number')}"

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"ℹ️  Return code for job {job_id} in SLURM API ({location.name}): {return_code}"
            )

        return int(return_code)

    @cachedmethod(
        lambda self: self._jobs_cache,
        key=partial(cachetools.keys.hashkey, "running_jobs"),
    )
    async def _get_running_jobs(self, location: ExecutionLocation) -> Collection[str]:
        service = self._get_service(location)

        r = _slurmapi_request(
            "GET",
            f"{service.api_address}/slurm/{service.api_version}/jobs",
            self._get_jwt_token(location),
        )

        # get all jobs
        running_jobs = r.json().get("jobs", [])

        # filter only pending, running, etc...
        running_jobs = [
            j
            for j in running_jobs
            if j.get("job_state")[0]
            in (
                "PENDING",
                "RUNNING",
                "SUSPENDED",
                "COMPLETING",
                "CONFIGURING",
                "RESIZING",
                "REVOKED",
                "SPECIAL_EXIT",
            )
        ]

        # get only job ids
        running_jobs = [str(j.get("job_id")) for j in running_jobs]

        # filter only those in scheduled jobs
        running_jobs = [j for j in running_jobs if j in self._scheduled_jobs]

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"ℹ️  Running jobs in SLURM API ({location.name}): {', '.join(running_jobs)}"
            )

        return running_jobs

    @property
    def _service_class(self) -> type[QueueManagerService]:
        return SlurmApiService

    async def _remove_jobs(
        self, location: ExecutionLocation, jobs: MutableSequence[str]
    ) -> None:
        #FIXME: when streamflow is forcibly stopped, the service is not available, therefore the location (and token) are not accessible.
        service = self._get_service(location)

        r = _slurmapi_request(
            "DELETE",
            f"{service.api_address}/slurm/{service.api_version}/jobs",
            self._get_jwt_token(location),
            json={"jobs": jobs},
        )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"ℹ️  Cancelled jobs {', '.join(jobs)} from SLURM API ({location.name})"
            )

    async def _run_batch_command(
        self,
        command: str,
        environment: MutableMapping[str, str] | None,
        job_name: str,
        location: ExecutionLocation,
        workdir: str | None = None,
        stdin: int | str | None = None,
        stdout: int | str = asyncio.subprocess.STDOUT,
        stderr: int | str = asyncio.subprocess.STDOUT,
        timeout: int | None = None,
    ) -> str:
        env = [f"{k}={v}" for k, v in (environment or {}).items()]
        env.append("PATH=/bin/:/usr/bin/:/sbin/:/usr/local/bin")

        job_cfg = {
            "script": command,
            "name": job_name,
            "environment": env,
            "time_limit": timeout,
            "current_working_directory": workdir,
            "standard_output": self._format_stream(stdout),
            "standard_error": self._format_stream(stdout),
            "standard_input": (
                shlex.quote(stdin)
                if stdin not in (None, asyncio.subprocess.DEVNULL)
                else None
            ),
        }

        service = self._get_service(location)
        for k, v in service.__dict__.items():
            if v is not None and k not in EXCLUDED_SERVICE_PARAMETERS:
                job_cfg[k] = v

        r = _slurmapi_request(
            "POST",
            f"{service.api_address}/slurm/{service.api_version}/job/submit",
            self._get_jwt_token(location),
            json={"job": job_cfg},
        )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"ℹ️  Submitted job {job_name} to SLURM API ({location.name}) with ID {r.json().get('job_id')}"
            )

        job_id = str(r.json().get("job_id"))

        return job_id
