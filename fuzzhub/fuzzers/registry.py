"""
File: fuzzhub/fuzzers/registry.py

Fuzzer registry for dynamic plugin loading.
"""

from typing import Dict, Type
from fuzzhub.fuzzers.base import BaseFuzzer


class FuzzerRegistry:
    _registry: Dict[str, Type[BaseFuzzer]] = {}

    @classmethod
    def register(cls, name: str, fuzzer_cls: Type[BaseFuzzer]) -> None:
        cls._registry[name] = fuzzer_cls

    @classmethod
    def get(cls, name: str) -> Type[BaseFuzzer]:
        if name not in cls._registry:
            raise ValueError(f"Fuzzer '{name}' not registered.")
        return cls._registry[name]

    @classmethod
    def list_available(cls):
        return list(cls._registry.keys())

# ----------------------------------------------------------------------
# FUZZERS
# ----------------------------------------------------------------------
# Dummy
from fuzzhub.fuzzers.dummy import DummyFuzzer
FuzzerRegistry.register("dummy", DummyFuzzer)

