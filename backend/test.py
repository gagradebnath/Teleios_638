import pytest
from tools import *
from tools.stats_analysis import StatsAnalysisTool

class TestToolsInitialization:
    """Test initialization of tools modules"""
    
    def test_stat_analysis_tool_initialization(self):
        """Test that StatAnalysisTool initializes correctly"""
        stat = StatsAnalysisTool()
        assert stat is not None
        assert isinstance(stat, StatsAnalysisTool)
    
    def test_stat_analysis_tool_has_required_attributes(self):
        """Test that StatAnalysisTool has expected attributes"""
        stat = StatsAnalysisTool()
        assert hasattr(stat, '__class__')
    
    def test_multiple_stat_analysis_instances(self):
        """Test creating multiple StatAnalysisTool instances"""
        stat1 = StatsAnalysisTool()
        stat2 = StatsAnalysisTool()
        assert stat1 is not stat2
        assert isinstance(stat1, StatsAnalysisTool)
        assert isinstance(stat2, StatsAnalysisTool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])