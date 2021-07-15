import pytest
import yaml
import json
import logging
from boddle import boddle
from webhook import read_config, get_module_logger, get_messages, read_request_from_file, do_post
import webhook


# @pytest.fixture()
# def context():
#    return read_config()

def test_read_config():
    t = read_config('./tests/test_multiple_create_rules_config.yaml')
    assert t['loglevel'] == 50


def test_get_messages_multiple_create_rules():
    webhook.config = read_config('./tests/test_multiple_create_rules_config.yaml')
    webhook.logger = get_module_logger("test_webhook", webhook.config['loglevel'])

    file = open('./tests/test_multiple_create_rules_result.yaml', 'r', encoding='utf-8')
    correct_res = yaml.safe_load(file)
    file.close()

    request = read_request_from_file('./tests/test_multiple_create_rules_request.json')
    test_res = get_messages(request)

    assert correct_res == test_res


def test_get_messages_email_substitution():
    webhook.config = read_config('./tests/test_email_substitution_config.yml')
    webhook.logger = get_module_logger("test_webhook", webhook.config['loglevel'])

    file = open('./tests/test_email_substitution_result.yml', 'r', encoding='utf-8')
    correct_res = yaml.safe_load(file)
    file.close()

    request = read_request_from_file('./tests/test_email_substitution_request.json')
    test_res = get_messages(request)

    assert correct_res == test_res


def test_do_post_valid_request():
    webhook.config = read_config('./tests/test_email_substitution_config.yml')
    webhook.logger = get_module_logger("test_webhook", webhook.config['loglevel'])

    file = open('./tests/test_email_substitution_result.yml', 'r', encoding='utf-8')
    result = yaml.safe_load(file)
    file.close()

    request = read_request_from_file('./tests/test_email_substitution_request.json')
    with boddle(json=request):
        assert do_post().body == json.dumps(result, ensure_ascii=False)


def test_do_post_invalid_request():
    webhook.config = read_config('./tests/test_email_substitution_config.yml')
    # set log level to CRITICAL to skip logging exceptions
    webhook.logger = get_module_logger("test_webhook", logging.CRITICAL)
    with boddle(body='{"invalid_json": true, }'):
        assert do_post().status_code == 400


def test_do_post_ncr_encoding():
    """
    Тест декодирования символов типа &#931; в юникод. Такие символы встречаются
    в author.name и description пример в test_ncr_encoding.json
    """
    webhook.config = read_config('./tests/test_email_substitution_config.yml')
    webhook.logger = get_module_logger("test_webhook", webhook.config['loglevel'])

    file = open('./tests/test_ncr_encoding_result.yml', 'r', encoding='utf-8')
    result = yaml.safe_load(file)
    file.close()

    request = read_request_from_file('./tests/test_ncr_encoding.json')
    with boddle(json=request):
        assert do_post().body == json.dumps(result, ensure_ascii=False)
