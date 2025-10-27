#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["/bin/sh", "-c"]

requirements: {}

inputs: 
  dependency_input:
    type: string
outputs: {}

arguments:
  - valueFrom: "echo completed step 3"

  