import pytest
from cash_sync import AllyImporter, CapitalOneImporter

def test_ally_importer_initialization():
    importer = AllyImporter()
    assert importer is not None

def test_capital_one_importer_initialization():
    importer = CapitalOneImporter()
    assert importer is not None

# Add more tests as needed 
