""" Tests for construction of a Pipeline """

import pytest
from pypiper import Pipeline, PipelineManager, Stage
from tests.helpers import assert_equal_dirpath, named_param, SafeTestPipeline


__author__ = "Vince Reuter"
__email__ = "vreuter@virginia.edu"



def test_pipeline_requires_stages_definition(tmpdir):
    """ To create a pipeline, define stages (execution steps). """

    class NoStagesPipeline(SafeTestPipeline):
        pass

    name = "test-pipe"

    # Sensitivity: test exception for bad case.
    with pytest.raises(TypeError):
        NoStagesPipeline(name=name, outfolder=tmpdir.strpath)
    # Specificity: test no exception for good case.
    _MinimalPipeline(name=name, outfolder=tmpdir.strpath)



class JustManagerArgument:
    """ A pipeline can be created with just a manager argument. """


    NAME_HOOK = "pl_mgr_name"


    @pytest.fixture
    def pl_mgr(self, request, get_pipe_manager):
        """ Provide each of this class's test cases with pipeline manager. """
        if self.NAME_HOOK in request.fixturenames:
            name = request.getfixturevalue(self.NAME_HOOK)
        else:
            name = "test-pipe"
        return get_pipe_manager(name=name)


    @named_param(
        argnames=NAME_HOOK, argvalues=["arbitrary-pipeline", "DummyPipe"])
    def test_pipeline_adopts_manager_name(self, pl_mgr_name, pl_mgr):
        """ If given just a manager, a pipeline uses the manager name. """
        pl = Pipeline(manager=pl_mgr)
        assert pl_mgr_name == pl_mgr.name
        assert pl_mgr_name == pl.name


    def test_pipeline_adopts_manager_output_folder(self, pl_mgr):
        """ Pipeline uses manager output folder if given just manager. """
        pl = Pipeline(manager=pl_mgr)
        assert pl_mgr.outfolder == pl.outfolder



class MinimalArgumentsWithoutManagerTests:
    """ Tests for pipeline constructor argument provision without manager. """


    def test_pipeline_creates_manager(self, tmpdir):
        """ If not passed a pipeline manager, a pipeline creates one. """
        empty = _MinimalPipeline(name="minimal", outfolder=tmpdir.strpath)
        assert isinstance(empty.manager, PipelineManager)


    @named_param("pipe_name", ["test-pipe", "DummyPipeline"])
    def test_manager_adopts_pipeline_name(self, pipe_name, tmpdir):
        """ Autogenerated pipeline manager uses pipeline's name. """
        pl = _MinimalPipeline(name=pipe_name, outfolder=tmpdir.strpath)
        assert pipe_name == pl.name
        assert pl.name == pl.manager.name


    def test_manager_adopts_pipeline_output_folder(self, tmpdir):
        """ Autogenerated pipeline manager uses pipeline's output folder. """
        pl = _MinimalPipeline(name="test-pipe", outfolder=tmpdir.strpath)
        assert_equal_dirpath(tmpdir.strpath, pl.outfolder)



class ConceptuallyOverlappingArgumentsTests:
    """
    Test cases in which pipeline's argument space is overspecified.

    Specifically, there are two main argument specification strategies for
    creating a pipeline, each of which is minimal in its own way. One is to
    directly pass a PipelineManager, and the other is to pass a name and a
    path to an output folder. The manager implies both the name and the
    output folder, and the name + output folder can be used in conjunction
    to create a pipeline manager if one's not passed. This class aims to test
    the outcomes of cases in which the combination of arguments passed to the
    pipeline constructor overspecifies the space defined by pipeline name,
    output folder path, and pipeline manager.

    """


    def test_same_name_for_manager_and_pipeline(
            self, tmpdir, get_pipe_manager):
        """ Pipeline name and manager with matching name is unproblematic. """
        name = "test-pipe"
        pm = get_pipe_manager(name=name, outfolder=tmpdir.strpath)
        pl = _MinimalPipeline(name=name, manager=pm)
        assert name == pl.manager.name


    def test_different_name_for_manager_and_pipeline(
            self, tmpdir, get_pipe_manager):
        """ If given, pipeline favors its own name over manager's. """
        manager_name = "manager"
        pipeline_name = "pipeline"
        pm = get_pipe_manager(name=manager_name, outfolder=tmpdir.strpath)
        pl = _MinimalPipeline(name=pipeline_name, manager=pm)
        assert pipeline_name == pl.name
        assert manager_name == pl.manager.name


    @named_param(
        "output_folder", argvalues=["test-output", "testing-output-folder"])
    def test_pipeline_ignores_outfolder_if_manager_is_passed(
            self, output_folder, tmpdir, get_pipe_manager):
        """ Manager's output folder trumps explicit output folder. """
        pm = get_pipe_manager(name="test-pipe", outfolder=tmpdir.strpath)
        pl = _MinimalPipeline(manager=pm, outfolder=output_folder)
        assert_equal_dirpath(tmpdir.strpath, pl.outfolder)


    def test_name_outfolder_and_manager(self, tmpdir, get_pipe_manager):
        """ Tests provision of all three primary pipeline arguments. """
        name = "test-pipe"
        pm = get_pipe_manager(name=name, outfolder=tmpdir.strpath)
        pl = _MinimalPipeline(name=name, manager=pm, outfolder=tmpdir.strpath)
        assert name == pl.name
        assert_equal_dirpath(tmpdir.strpath, pl.outfolder)
        assert pm == pl.manager



def test_pipeline_requires_either_manager_or_outfolder():
    """ Pipeline must be passed pipeline manager or output folder. """
    with pytest.raises(TypeError):
        _MinimalPipeline()



def test_empty_pipeline_manager_name_and_no_explicit_pipeline_name(
        tmpdir, get_pipe_manager):
    """ If no name's passed to pipeline, the manager must have valid name. """
    pm = get_pipe_manager(name="", outfolder=tmpdir.strpath)
    with pytest.raises(ValueError):
        _MinimalPipeline(manager=pm)



class AnonymousFunctionStageTests:
    """ Tests for anonymous function as a pipeline stage. """


    def test_anonymous_stage_without_name_is_prohibited(self, tmpdir):
        """ Anonymous function as Stage must be paired with name. """
        with pytest.raises(TypeError):
            _AnonymousStageWithoutNamePipeline(
                    name="test-pipe", outfolder=tmpdir.strpath)


    def test_anonymous_stage_with_name_is_permitted(self, tmpdir):
        """ Anonymous function as Stage must be paired with name. """
        _AnonymousStageWithNamePipeline(
                name="test-pipe", outfolder=tmpdir.strpath)



class _AnonymousStageWithoutNamePipeline(SafeTestPipeline):
    """ Anonymous function as stage is prohibited unless paired with name. """
    def stages(self):
        return [lambda: None]



class _AnonymousStageWithNamePipeline(SafeTestPipeline):
    """ Anonymous function as Stage is allowed if wrapped with a name. """
    def stages(self):
        return [("NullStage", lambda: None)]



@pytest.fixture
def empty_pipeline(request):
    """ Provide test case with minimal pipeline instance. """
    if "pipe_name" in request.fixturenames:
        name = request.getfixturevalue("pipe_name")
    else:
        name = "minimal"
    return _MinimalPipeline(name)



class _MinimalPipeline(SafeTestPipeline):
    """ Minimal pipeline declaration. """

    def stages(self):
        """ Sham stages definition. """
        return [_do_nothing]



def _do_nothing():
    return