"""Post-freeze visualization controls; no target integrations."""
import pytest
from scripts import plot_exp498_boundary_transport as plot


@pytest.mark.parametrize("value",[{},dict(experiment_id="EXP-498",passed=False),
    dict(experiment_id="EXP-498",passed=True,source_commit="wrong-source")])
def test_incomplete_or_unbound_result_cannot_be_plotted(value):
    with pytest.raises(ValueError,match="audited"):
        plot.validate(value)


def test_plotted_rows_keep_failures_and_all_event_indices():
    data = dict(rows=[dict(id="empty",predecessors=[],geometry=dict(analysis=None)),
        dict(id="failed",geometry=dict(analysis=dict(qualified=False)),predecessors=[
            dict(eligible=True,event=dict(state=[1.,2.,3.]),windows=[dict(state_distances=[1.,2.,3.,4.,5.,6.]),
                dict(state_distances=[6.,5.,4.,3.,2.,1.])])])])
    assert plot.plot_rows(data) == [dict(id="empty",qualified=False,states=[],worst_distances=None),
        dict(id="failed",qualified=False,states=[[1.,2.,3.]],worst_distances=[6.,5.,4.,4.,5.,6.])]
