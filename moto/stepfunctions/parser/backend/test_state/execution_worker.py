from typing import Optional

from moto.stepfunctions.parser.asl.component.eval_component import EvalComponent
from moto.stepfunctions.parser.asl.eval.environment import Environment
from moto.stepfunctions.parser.asl.eval.event.event_manager import (
    EventHistoryContext,
)
from moto.stepfunctions.parser.asl.eval.states import (
    ContextObjectData,
    ExecutionData,
    StateMachineData,
)
from moto.stepfunctions.parser.asl.eval.test_state.environment import (
    TestStateEnvironment,
)
from moto.stepfunctions.parser.asl.parse.test_state.asl_parser import (
    TestStateAmazonStateLanguageParser,
)
from moto.stepfunctions.parser.backend.execution_worker import SyncExecutionWorker


class TestStateExecutionWorker(SyncExecutionWorker):
    env: Optional[TestStateEnvironment]

    def _get_evaluation_entrypoint(self) -> EvalComponent:
        return TestStateAmazonStateLanguageParser.parse(
            self._evaluation_details.state_machine_details.definition
        )[0]

    def _get_evaluation_environment(self) -> Environment:
        return TestStateEnvironment(
            aws_execution_details=self._evaluation_details.aws_execution_details,
            execution_type=self._evaluation_details.state_machine_details.typ,
            context=ContextObjectData(
                Execution=ExecutionData(
                    Id=self._evaluation_details.execution_details.arn,
                    Input=self._evaluation_details.execution_details.inpt,
                    Name=self._evaluation_details.execution_details.name,
                    RoleArn=self._evaluation_details.execution_details.role_arn,
                    StartTime=self._evaluation_details.execution_details.start_time,
                ),
                StateMachine=StateMachineData(
                    Id=self._evaluation_details.state_machine_details.arn,
                    Name=self._evaluation_details.state_machine_details.name,
                ),
            ),
            event_history_context=EventHistoryContext.of_program_start(),
            cloud_watch_logging_session=self._cloud_watch_logging_session,
            activity_store=self._activity_store,
        )
