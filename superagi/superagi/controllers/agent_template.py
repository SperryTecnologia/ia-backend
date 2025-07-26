from fastapi import APIRouter, Depends, HTTPException
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent import Agent
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.agent_template import AgentTemplate
from superagi.models.agent_template_config import AgentTemplateConfig
from superagi.models.tool import Tool
from superagi.helper.auth import get_user_organisation, get_current_user
from superagi.models.db import DBSession

router = APIRouter()

@router.post("/publish_template/agent_execution_id/{agent_execution_id}", status_code=201)
def publish_template(
    agent_execution_id: str,
    organisation=Depends(get_user_organisation),
    user=Depends(get_current_user)
):
    """
    Publish an agent execution as a template.

    Args:
        agent_execution_id (str): The ID of the agent execution to save as a template.
        organisation (Depends): Dependency to get the user organisation.
        user (Depends): Dependency to get the user.

    Returns:
        dict: The saved agent template.

    Raises:
        HTTPException (status_code=404): If the agent or agent execution configurations are not found.
    """
    if agent_execution_id == "undefined":
        raise HTTPException(status_code=404, detail="Agent Execution Id undefined")

    session = DBSession()
    try:
        agent_executions = AgentExecution.get_agent_execution_from_id(session, agent_execution_id)
        if agent_executions is None:
            raise HTTPException(status_code=404, detail="Agent Execution not found")

        agent_id = agent_executions.agent_id
        agent = session.query(Agent).filter(Agent.id == agent_id).first()
        if agent is None:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent_execution_configurations = session.query(AgentExecutionConfiguration).filter(
            AgentExecutionConfiguration.agent_execution_id == agent_execution_id
        ).all()

        if not agent_execution_configurations:
            raise HTTPException(status_code=404, detail="Agent execution configurations not found")

        agent_template = AgentTemplate(
            name=agent.name,
            description=agent.description,
            agent_workflow_id=agent.agent_workflow_id,
            organisation_id=organisation.id
        )
        session.add(agent_template)
        session.commit()

        main_keys = AgentTemplate.main_keys()
        for config in agent_execution_configurations:
            if config.key not in main_keys:
                continue

            config_value = config.value
            if config.key == "tools":
                config_value = str(Tool.convert_tool_ids_to_names(session, eval(config.value)))

            session.add(AgentTemplateConfig(
                agent_template_id=agent_template.id,
                key=config.key,
                value=config_value
            ))

        session.add_all([
            AgentTemplateConfig(agent_template_id=agent_template.id, key="status", value="UNDER REVIEW"),
            AgentTemplateConfig(agent_template_id=agent_template.id, key="Contributor Name", value=user.name),
            AgentTemplateConfig(agent_template_id=agent_template.id, key="Contributor Email", value=user.email)
        ])

        session.commit()
        return agent_template.to_dict()

    finally:
        session.close()
