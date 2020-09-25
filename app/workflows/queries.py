from .models import db, Workflow, WorkflowPipeline, WorkflowPipelineDependency
from sqlalchemy import and_, or_
import networkx as nx

from .models import Workflow
from .schemas import SearchWorkflowsSchema


def find_workflow(uuid):
    """ Find a workflow. """
    return Workflow.query.filter(
        and_(
            Workflow.uuid == uuid,
            Workflow.is_deleted == False,
        )
    ).one_or_none()


def find_workflows(uuids=None):
    """ Find all workflows, or a list of them. """
    query = Workflow.query.filter(Workflow.is_deleted == False)

    if uuids is not None:
        data = SearchWorkflowsSchema().load(uuids)
        query = query.filter(Workflow.uuid.in_(map(str, data["uuids"])))

    return query


def find_workflow_pipeline(workflow_pipeline_uuid):
    """ Find a WorkflowPipeline. """
    return (
        WorkflowPipeline.query.join(Workflow)
        .filter(
            and_(
                WorkflowPipeline.uuid == workflow_pipeline_uuid,
                Workflow.is_deleted == False,
            )
        )
        .one_or_none()
    )


def find_workflow_pipeline_dependencies(workflow_uuid):
    workflow_pipeline_sq = (
        db.session.query(WorkflowPipeline.id)
        .join(Workflow)
        .filter(
            Workflow.is_deleted == False,
            Workflow.uuid == workflow_uuid,
        )
        .subquery("workflow_pipeline_sq")
    )
    return WorkflowPipelineDependency.query.filter(
        or_(
            WorkflowPipelineDependency.from_workflow_pipeline_id.in_(
                workflow_pipeline_sq
            ),
            WorkflowPipelineDependency.to_workflow_pipeline_id.in_(
                workflow_pipeline_sq
            ),
        )
    )


def find_workflow_pipelines(workflow_uuid):
    """ Find all workflow pipelines, or a list of them. """
    return WorkflowPipeline.query.filter(Workflow.workflow_id == workflow_uuid)


def is_dag(workflow, from_workflow_pipeline=None, to_workflow_pipeline=None):
    """Returns True if the graph supplied a directed acyclic graph and adding a
    new edge would not introduce a cycle."""

    dependencies = find_workflow_pipeline_dependencies(workflow.uuid)
    digraph = nx.DiGraph()
    for dependency in dependencies:
        digraph.add_edge(
            dependency.from_workflow_pipeline_id, dependency.to_workflow_pipeline_id
        )

    if from_workflow_pipeline is not None and to_workflow_pipeline is not None:
        digraph.add_edge(from_workflow_pipeline.id, to_workflow_pipeline.id)

    return nx.is_directed_acyclic_graph(digraph)


def find_pipeline_runs_for_workflow_run(workflow_run):
    workflow_pipeline_runs = [wpr for wpr in workflow_run.workflow_pipeline_runs]
    return [wpr.pipeline_run for wpr in workflow_pipeline_runs]


def find_dest_workflow_runs(workflow_pipeline_run):
    workflow_run = workflow_pipeline_run.workflow_run
    # TODO this should be a sql query for optimal speed -- or I should be
    # able to find this from the workflow_run itself?
    result = []
    for dest_wp in workflow_pipeline_run.workflow_pipeline.dest_workflow_pipelines:
        result.extend([
            wpr.pipeline_run
            for wpr in dest_wp.to_workflow_pipeline.workflow_pipeline_runs
            if wpr.workflow_run == workflow_run
        ])
    return result


def find_source_workflow_runs(workflow_pipeline_run):
    workflow_run = workflow_pipeline_run.workflow_run
    # TODO this should be a sql query for optimal speed -- or I should be
    # able to find this from the workflow_run itself?
    result = []
    for dest_wp in workflow_pipeline_run.workflow_pipeline.source_workflow_pipelines:
        result.extend([
            wpr.pipeline_run
            for wpr in dest_wp.from_workflow_pipeline.workflow_pipeline_runs
            if wpr.workflow_run == workflow_run
        ])
    return result
