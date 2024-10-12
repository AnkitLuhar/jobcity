import pytest
from unittest import mock
from pytest_mock import mocker
from src.jobcity_easy_applier import AIHawkEasyApplier


@pytest.fixture
def mock_driver():
    """Fixture to mock Selenium WebDriver."""
    return mock.Mock()


@pytest.fixture
def mock_gpt_answerer():
    """Fixture to mock GPT Answerer."""
    return mock.Mock()


@pytest.fixture
def mock_resume_generator_manager():
    """Fixture to mock Resume Generator Manager."""
    return mock.Mock()


@pytest.fixture
def easy_applier(mock_driver, mock_gpt_answerer, mock_resume_generator_manager):
    """Fixture to initialize AIHawkEasyApplier with mocks."""
    return AIHawkEasyApplier(
        driver=mock_driver,
        resume_dir="/path/to/resume",
        set_old_answers=[('Question 1', 'Answer 1', 'Type 1')],
        gpt_answerer=mock_gpt_answerer,
        resume_generator_manager=mock_resume_generator_manager
    )


def test_initialization(mocker):
    """Test that AIHawkEasyApplier is initialized correctly."""
    # Mock os.path.exists to return True
    mocker.patch('os.path.exists', return_value=True)

    mock_driver = mocker.Mock()
    mock_gpt_answerer = mocker.Mock()
    mock_resume_generator_manager = mocker.Mock()

    easy_applier = AIHawkEasyApplier(
        driver=mock_driver,
        resume_dir="/path/to/resume",
        set_old_answers=[('Question 1', 'Answer 1', 'Type 1')],
        gpt_answerer=mock_gpt_answerer,
        resume_generator_manager=mock_resume_generator_manager
    )

    assert easy_applier.resume_path == "/path/to/resume"
    assert len(easy_applier.set_old_answers) == 1
    assert easy_applier.gpt_answerer is not None
    assert easy_applier.resume_generator_manager is not None


def test_apply_to_job_success(mocker):
    """Test successfully applying to a job."""
    mock_driver = mocker.Mock()
    mock_gpt_answerer = mocker.Mock()
    mock_resume_generator_manager = mocker.Mock()
    easy_applier = AIHawkEasyApplier(
        driver=mock_driver,
        resume_dir="/path/to/resume",
        set_old_answers=[],
        gpt_answerer=mock_gpt_answerer,
        resume_generator_manager=mock_resume_generator_manager
    )
    mock_job = mocker.Mock()

    # Mock job_apply so we don't actually try to apply
    mocker.patch.object(easy_applier, 'job_apply')

    easy_applier.apply_to_job(mock_job)
    easy_applier.job_apply.assert_called_once_with(mock_job)


def test_apply_to_job_failure(mocker):
    """Test failure while applying to a job."""
    mock_driver = mocker.Mock()
    mock_gpt_answerer = mocker.Mock()
    mock_resume_generator_manager = mocker.Mock()
    easy_applier = AIHawkEasyApplier(
        driver=mock_driver,
        resume_dir="/path/to/resume",
        set_old_answers=[],
        gpt_answerer=mock_gpt_answerer,
        resume_generator_manager=mock_resume_generator_manager
    )
    mock_job = mocker.Mock()
    mocker.patch.object(easy_applier, 'job_apply',
                        side_effect=Exception("Test error"))

    with pytest.raises(Exception, match="Test error"):
        easy_applier.apply_to_job(mock_job)

    easy_applier.job_apply.assert_called_once_with(mock_job)


def test_check_for_premium_redirect_no_redirect(mocker):
    """Test that check_for_premium_redirect works when there's no redirect."""
    mock_driver = mocker.Mock()
    mock_gpt_answerer = mocker.Mock()
    mock_resume_generator_manager = mocker.Mock()
    easy_applier = AIHawkEasyApplier(
        driver=mock_driver,
        resume_dir="/path/to/resume",
        set_old_answers=[],
        gpt_answerer=mock_gpt_answerer,
        resume_generator_manager=mock_resume_generator_manager
    )
    mock_job = mocker.Mock()
    easy_applier.driver.current_url = "https://www.linkedin.com/jobs/view/1234"

    easy_applier.check_for_premium_redirect(mock_job)
    easy_applier.driver.get.assert_not_called()


def test_check_for_premium_redirect_with_redirect(mocker):
    """Test that check_for_premium_redirect handles AIHawk Premium redirects."""
    mock_driver = mocker.Mock()
    mock_gpt_answerer = mocker.Mock()
    mock_resume_generator_manager = mocker.Mock()
    easy_applier = AIHawkEasyApplier(
        driver=mock_driver,
        resume_dir="/path/to/resume",
        set_old_answers=[],
        gpt_answerer=mock_gpt_answerer,
        resume_generator_manager=mock_resume_generator_manager
    )
    mock_job = mocker.Mock()
    easy_applier.driver.current_url = "https://www.linkedin.com/premium"
    mock_job.link = "https://www.linkedin.com/jobs/view/1234"

    with pytest.raises(Exception, match="Redirected to AIHawk Premium page and failed to return"):
        easy_applier.check_for_premium_redirect(mock_job)

    # Verify that it attempted to return to the job page 3 times
    assert easy_applier.driver.get.call_count == 3
