import pytest
from core.utils.helpers import validate_cpf


class TestValidateCPF:
    
    def test_valid_cpf(self):
        assert validate_cpf('11144477735') is True
        assert validate_cpf('52998224725') is True
        assert validate_cpf('01234567890') is True
    
    def test_invalid_cpf_wrong_digits(self):
        assert validate_cpf('11144477734') is False
        assert validate_cpf('12345678901') is False
    
    def test_invalid_cpf_all_same_digits(self):
        assert validate_cpf('11111111111') is False
        assert validate_cpf('00000000000') is False
        assert validate_cpf('99999999999') is False
    
    def test_invalid_cpf_wrong_length(self):
        assert validate_cpf('123') is False
        assert validate_cpf('123456789012') is False
        assert validate_cpf('') is False
    
    def test_invalid_cpf_non_numeric(self):
        assert validate_cpf('11144477a35') is False
        assert validate_cpf('abc') is False
    
    def test_invalid_cpf_none(self):
        assert validate_cpf(None) is False
