import logging
import requests as r
from connectors.base_connector import BaseConnector


def assert_token_set(method):
    """Makes sure we have tokens."""
    def _assert_tokens(self, *method_args, **method_kwargs):
        assert self.tokens, "No app tokens available, please register the app!"
        return method(self, *method_args, **method_kwargs)
    return _assert_tokens


class RallyConnector(BaseConnector):
    """Connect to the Rally API for NFT and user info."""
    def __init__(self, cfg):
        super().__init__(cfg)
        self.logger = logging.getLogger(__name__)
        self.api_url = cfg['rally']['api-url']
        self.coin = cfg['rally']['coin']
        self.nft_template_ids = cfg['rally']['nft-template-ids']
        self.tokens = None

        self.logger.info(
            f'Rally connector looking for coin {self.coin} \n' +
            f'and the following NFT templates:\n {self.nft_template_ids}'
        )

    def set_app_tokens(self, token_dict):
        assert 'access_token' in token_dict, 'Missing access token!'
        assert 'refresh_token' in token_dict, 'Missing refresh token!'
        self.tokens = token_dict
        self.auth_header = {'Authorization': 'Bearer ' + token_dict['access_token']}

    # @assert_token_set
    def get_nft_templates(self):
        templates = []
        for id_ in self.nft_template_ids:
            resp = r.get(
                self.api_url + '/api/nft-templates/' + id_
            )
            self.logger.debug(resp.json())
            templates.append(resp.json())
        return templates

    def get_nft(self, nft_template_id):
        return r.get(
            self.api_url + '/api/nfts',
            params={'nftTemplateId': nft_template_id}
        ).json()

    def get_account_info(self, username):
        return r.get(
            self.api_url + '/api/accounts/' + username
        ).json()
