#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["/bin/sh", "-c"]

requirements:
  - class: ShellCommandRequirement

inputs: {}
outputs: {}

arguments:
  - valueFrom: "hostname"

  