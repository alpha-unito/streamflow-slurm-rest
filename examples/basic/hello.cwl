#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["/bin/sh", "-c"]

inputs: {}

outputs:
  outputfile:
    type: stdout

stdout: output.txt

arguments:
  - valueFrom: "hostname"


  