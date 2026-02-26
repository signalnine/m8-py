import pytest
from m8py.validate import validate, Severity, ValidationIssue
from m8py.models.song import Song
from m8py.models.song_step import SongStep
from m8py.models.chain import Chain, ChainStep
from m8py.models.phrase import Phrase, PhraseStep
from m8py.models.instrument import Sampler, SynthCommon, EmptyInstrument
from m8py.format.constants import EMPTY, N_PHRASES, N_CHAINS, N_INSTRUMENTS


class TestValidation:
    def test_default_song_no_issues(self):
        song = Song()
        issues = validate(song)
        assert len(issues) == 0

    def test_tempo_too_low(self):
        song = Song()
        song.tempo = 0.5
        issues = validate(song)
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert any("tempo" in i.path for i in errors)

    def test_tempo_too_high(self):
        song = Song()
        song.tempo = 900.0
        issues = validate(song)
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert any("tempo" in i.path for i in errors)

    def test_tempo_valid_boundary(self):
        song = Song()
        song.tempo = 1.0
        assert len(validate(song)) == 0
        song.tempo = 800.0
        assert len(validate(song)) == 0

    def test_chain_reference_out_of_range(self):
        song = Song()
        # Use N_CHAINS + 1 since N_CHAINS (255) == EMPTY (0xFF) would be skipped
        song.song_steps[0] = SongStep(tracks=[N_CHAINS + 1] + [EMPTY] * 7)
        issues = validate(song)
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert any("chain reference" in i.message for i in errors)

    def test_phrase_reference_out_of_range(self):
        song = Song()
        # Use N_PHRASES + 1 since N_PHRASES (255) == EMPTY (0xFF) would be skipped
        song.chains[0] = Chain(steps=[ChainStep(phrase=N_PHRASES + 1)] + [ChainStep() for _ in range(15)])
        issues = validate(song)
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert any("phrase reference" in i.message for i in errors)

    def test_instrument_reference_out_of_range(self):
        song = Song()
        song.phrases[0] = Phrase(steps=[PhraseStep(instrument=N_INSTRUMENTS)] + [PhraseStep() for _ in range(15)])
        issues = validate(song)
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert any("instrument reference" in i.message for i in errors)

    def test_sampler_empty_path_warning(self):
        song = Song()
        song.instruments[0] = Sampler(common=SynthCommon(name="NoPath"))
        issues = validate(song)
        warnings = [i for i in issues if i.severity == Severity.WARNING]
        assert any("sample_path" in i.message for i in warnings)

    def test_sampler_with_path_no_warning(self):
        song = Song()
        song.instruments[0] = Sampler(
            common=SynthCommon(name="HasPath"),
            sample_path="/Samples/kick.wav"
        )
        issues = validate(song)
        warnings = [i for i in issues if i.severity == Severity.WARNING]
        assert not any("sample_path" in i.message for i in warnings)

    def test_name_too_long_warning(self):
        song = Song()
        song.name = "VeryLongSongName"  # > 11 chars
        issues = validate(song)
        warnings = [i for i in issues if i.severity == Severity.WARNING]
        assert any("truncated" in i.message for i in warnings)

    def test_empty_references_are_valid(self):
        """EMPTY (0xFF) references should not trigger errors."""
        song = Song()
        # Default song has EMPTY everywhere - should be valid
        issues = validate(song)
        assert len(issues) == 0

    def test_validation_issue_str(self):
        issue = ValidationIssue(Severity.ERROR, "song.tempo", "too fast")
        assert "[error] song.tempo: too fast" == str(issue)

    def test_byte_field_overflow(self):
        song = Song()
        song.transpose = 300  # > 255
        issues = validate(song)
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert any("transpose" in i.path for i in errors)
