from scripts.audit_exp227_exact_source_identity import SCHEMA


def test_exp227_exact_source_identity_schema_is_versioned():
    assert SCHEMA == "butterfly.exp227-exact-source-identity-manifest.v1"
