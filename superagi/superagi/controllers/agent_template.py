@router.post("/publish_template/agent_execution_id/{agent_execution_id}", status_code=201)

def publish_template(request: Request, agent_execution_id: str, organisation=Depends(get_user_organisation), user=Depends(get_current_user)):

    if agent_execution_id == "undefined":

        raise HTTPException(status_code=404, detail="Agent Execution Id undefined")

    agent_executions = AgentExecution.get_agent_execution_from_id(db.session, agent_execution_id)

    if agent_executions is None:

        raise HTTPException(status_code=404, detail="Agent Execution not found")

    agent_id = agent_executions.agent_id

    agent = db.session.query(Agent).filter(Agent.id == agent_id).first()

    if agent is None:

        raise HTTPException(status_code=404, detail="Agent not found")

    agent_execution_configurations = db.session.query(AgentExecutionConfiguration).filter(

        AgentExecutionConfiguration.agent_execution_id == agent_execution_id).all()

    if not agent_execution_configurations:

        raise HTTPException(status_code=404, detail="Agent execution configurations not found")

    agent_template = AgentTemplate(

        name=agent.name,

        description=agent.description,

        agent_workflow_id=agent.agent_workflow_id,

        organisation_id=organisation.id

    )

    db.session.add(agent_template)

    db.session.commit()

    main_keys = AgentTemplate.main_keys()

    for config in agent_execution_configurations:

        config_value = config.value

        if config.key not in main_keys:

            continue

        if config.key == "tools":

            config_value = str(Tool.convert_tool_ids_to_names(db, eval(config.value)))

        db.session.add(AgentTemplateConfig(

            agent_template_id=agent_template.id,

            key=config.key,

            value=config_value

        ))

    db.session.add_all([

        AgentTemplateConfig(agent_template_id=agent_template.id, key="status", value="UNDER REVIEW"),

        AgentTemplateConfig(agent_template_id=agent_template.id, key="Contributor Name", value=user.name),

        AgentTemplateConfig(agent_template_id=agent_template.id, key="Contributor Email", value=user.email)

    ])

    db.session.commit()

    db.session.flush()

    return agent_template.to_dict()
@router.post("/publish_template/agent_execution_id/{agent_execution_id}", status_code=201)

def publish_template(request: Request, agent_execution_id: str, organisation=Depends(get_user_organisation), user=Depends(get_current_user)):

    if agent_execution_id == "undefined":

        raise HTTPException(status_code=404, detail="Agent Execution Id undefined")

    agent_executions = AgentExecution.get_agent_execution_from_id(db.session, agent_execution_id)

    if agent_executions is None:

        raise HTTPException(status_code=404, detail="Agent Execution not found")

    agent_id = agent_executions.agent_id

    agent = db.session.query(Agent).filter(Agent.id == agent_id).first()

    if agent is None:

        raise HTTPException(status_code=404, detail="Agent not found")

    agent_execution_configurations = db.session.query(AgentExecutionConfiguration).filter(

        AgentExecutionConfiguration.agent_execution_id == agent_execution_id).all()

    if not agent_execution_configurations:

        raise HTTPException(status_code=404, detail="Agent execution configurations not found")

    agent_template = AgentTemplate(

        name=agent.name,

        description=agent.description,

        agent_workflow_id=agent.agent_workflow_id,

        organisation_id=organisation.id

    )

    db.session.add(agent_template)

    db.session.commit()

    main_keys = AgentTemplate.main_keys()

    for config in agent_execution_configurations:

        config_value = config.value

        if config.key not in main_keys:

            continue

        if config.key == "tools":

            config_value = str(Tool.convert_tool_ids_to_names(db, eval(config.value)))

        db.session.add(AgentTemplateConfig(

            agent_template_id=agent_template.id,

            key=config.key,

            value=config_value

        ))

    db.session.add_all([

        AgentTemplateConfig(agent_template_id=agent_template.id, key="status", value="UNDER REVIEW"),

        AgentTemplateConfig(agent_template_id=agent_template.id, key="Contributor Name", value=user.name),

        AgentTemplateConfig(agent_template_id=agent_template.id, key="Contributor Email", value=user.email)

    ])

    db.session.commit()

    db.session.flush()

    return agent_template.to_dict()
