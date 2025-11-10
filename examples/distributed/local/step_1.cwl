#!/usr/bin/env cwl-runner

cwlVersion: v1.2
class: CommandLineTool

baseCommand: ["/bin/sh", "-c"]

requirements:
  - class: InlineJavascriptRequirement

inputs: {}
outputs: 
  dependency_output:
    type: string
    outputBinding:
      outputEval: "any string"

stdout: output.txt

arguments:
  - valueFrom: "echo completed step 1"

  