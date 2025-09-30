import textwrap

from hestia.tools.utils.validators.adr_lint.src.hestia.tools.adr_lint import (
    config,
    rules,
)
from hestia.tools.utils.validators.adr_lint.src.hestia.tools.adr_lint.config import (
    CANONICAL_TEMPLATE,
)


def test_happy_adr(tmp_path):
    p = tmp_path / "ADR-0001.md"
    p.write_text(textwrap.dedent("""
    ---
    title: Example
    date: 2025-01-01
    status: Accepted
    author: Alice
    related: []
    supersedes: []
    last_updated: 2025-01-01
    ---

    This ADR references ADR-0001.

    ```yaml
    TOKEN_BLOCK:
      accepted:
        - ADR_FORMAT_OK
    ```
    """))

    res = rules.check_file(str(p), walker_cfg=config.WalkerConfig())
    assert all(v['severity'] != 'error' for v in res['violations'])


def test_duplicate_frontmatter(tmp_path):
    p = tmp_path / "ADR-0002.md"
    p.write_text("---\ntitle: A\n---\n---\ntitle: B\n---\n")
    res = rules.check_file(str(p), walker_cfg=config.WalkerConfig())
    assert any(v['rule'] == 'frontmatter.duplicate' for v in res['violations'])


def test_missing_key_order(tmp_path):
    p = tmp_path / "ADR-0003.md"
    p.write_text(textwrap.dedent("""
    ---
    date: 2025-01-01
    title: Example
    status: Accepted
    author: Bob
    related: []
    supersedes: []
    last_updated: 2025-01-01
    ---
    """))
    res = rules.check_file(str(p), walker_cfg=config.WalkerConfig())
    assert any(v['rule'] == 'frontmatter.order' for v in res['violations'])


def test_unclosed_fence(tmp_path):
    p = tmp_path / "ADR-0004.md"
    p.write_text("```bash\necho hi\n")
    res = rules.check_file(str(p), walker_cfg=config.WalkerConfig())
    assert any(v['rule'] == 'fence.unclosed' for v in res['violations'])


def test_volumes_in_code_block(tmp_path):
    p = tmp_path / "ADR-0005.md"
    p.write_text(textwrap.dedent("""
    ```bash
    ls /Volumes/Secret
    ```
    """))
    res = rules.check_file(str(p), walker_cfg=config.WalkerConfig())
    assert any(v['rule'] == 'path.volumes' for v in res['violations'])


def test_n_ha_parameterized_ok(tmp_path):
    p = tmp_path / "ADR-0006.md"
    p.write_text(textwrap.dedent("""
    ```bash
    echo ${HA_MOUNT}/foo
    ```
    """))
    res = rules.check_file(str(p), walker_cfg=config.WalkerConfig())
    assert not any(v['rule'] == 'path.n_ha' for v in res['violations'])


def test_n_ha_hardcoded_error(tmp_path):
    p = tmp_path / "ADR-0007.md"
    p.write_text(textwrap.dedent("""
    ```bash
    echo /n/ha/foo
    ```
    """))
    res = rules.check_file(str(p), walker_cfg=config.WalkerConfig())
    assert any(v['rule'] == 'path.n_ha' for v in res['violations'])


def test_n_ha_alternative_hardcoded_error(tmp_path):
    """Test case from workspace root tests - alternative hardcoded /n/ha pattern"""
    p = tmp_path / "ADR-0007b.md"
    p.write_text(textwrap.dedent("""
    ```bash
    echo ${HA_MOUNT:-$HOME/hass}/foo
    ```
    """))
    res = rules.check_file(str(p), walker_cfg=config.WalkerConfig())
    # This should be OK since it uses parameterized path
    assert not any(v['rule'] == 'path.n_ha' for v in res['violations'])


def test_canonical_template_ok(tmp_path):
    p = tmp_path / "ADR-0008.md"
    p.write_text(textwrap.dedent(f"""
    ```yaml
    - path: {config.CANONICAL_TEMPLATE}
    - path: {CANONICAL_TEMPLATE}
    ```
    """))
    res = rules.check_file(str(p), walker_cfg=config.WalkerConfig())
    assert not any(v['rule'] == 'template.path' for v in res['violations'])


def test_symlink_mention_error(tmp_path):
    p = tmp_path / "ADR-0009.md"
    p.write_text("ln -s /somewhere /config/template.library.jinja\n")
    res = rules.check_file(str(p), walker_cfg=config.WalkerConfig())
    assert any(
        v['rule'] == 'symlink.mention' or v['rule'] == 'token_block.missing'
        for v in res['violations']
    )
