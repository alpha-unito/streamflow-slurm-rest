cwlVersion: v1.2
class: Workflow

requirements:
  InlineJavascriptRequirement: {}

inputs: 
  streamflow_path:
    type: string
  streamflow_workflow:
    type: string
outputs: {}

steps:
  step_1:
    in: {}
    run: step_1.cwl
    out: [dependency_output]
  step_2:
    in:
      streamflow_path: streamflow_path
      streamflow_workflow: streamflow_workflow
      dependency_input: step_1/dependency_output
    run: step_2.cwl
    out: [dependency_output]
  step_3:
    in: 
      dependency_input: step_2/dependency_output
    run: step_3.cwl
    out: []