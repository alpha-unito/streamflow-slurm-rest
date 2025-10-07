#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["/bin/sh", "-c"]

requirements:
  - class: ShellCommandRequirement

inputs: {}
outputs: 
  output_file:
    type: stdout

stdout: output.txt

arguments:
  - valueFrom: "hostname"
    shellQuote: false

  