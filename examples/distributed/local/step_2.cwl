#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["/bin/sh", "-c"]

requirements:
  - class: InlineJavascriptRequirement

inputs: 
  streamflow_path:
    type: string
  streamflow_workflow:
    type: string
  dependency_input:
    type: string
outputs: 
# ⚠️ IMPORTANT: Because of limitations with the slurm rest API connector this output must be named 'dependency_output'
  dependency_output:
    type: string

arguments:
  - valueFrom: "$(inputs.streamflow_path) run $(inputs.streamflow_workflow)"
    shellQuote: true

  