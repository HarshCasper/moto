from moto.stepfunctions.parser.asl.component.common.jsonata.jsonata_template_value import (
    JSONataTemplateValue,
)
from moto.stepfunctions.parser.asl.component.eval_component import EvalComponent
from moto.stepfunctions.parser.asl.eval.environment import Environment


class Output(EvalComponent):
    jsonata_template_value: JSONataTemplateValue

    def __init__(self, jsonata_template_value: JSONataTemplateValue):
        self.jsonata_template_value = jsonata_template_value

    def _eval_body(self, env: Environment) -> None:
        self.jsonata_template_value.eval(env=env)
        output_value = env.stack.pop()
        env.states.reset(input_value=output_value)
